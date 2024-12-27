import os
import shutil
from datetime import datetime
from typing import List

from avstack.config import AGENTS, ConfigDict
from mate.config import MATE


class TrustSimulation:
    def __init__(
        self,
        t0: datetime,
        agents: List[ConfigDict],
        command_center: ConfigDict,
        trust_estimator: ConfigDict,
        log_dir: str = "last_run",
        log_trust: bool = True,
    ):
        self.log_dir = log_dir
        if os.path.exists(self.log_dir):
            shutil.rmtree(self.log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        self.t0 = t0

        # agents
        self.agents = {agent["ID"]: AGENTS.build(agent) for agent in agents}
        self.command_center = AGENTS.build(command_center)

        # trust estimator
        if log_trust:
            trust_estimator["post_hooks"] = [
                {"type": "TrustLogger", "output_folder": os.path.join(log_dir, "trust")}
            ]
        self.trust_estimator = MATE.build(trust_estimator)

    def __call__(self, data):
        """Step the simulation forward in time"""

        # run local agent pipelines
        agent_platforms = {}
        agent_fovs_global = {}
        agent_dets_global = {}
        agent_tracks_global = {}
        for agent_ID in self.agents:
            # get sensor data
            # HACK: fix that it is lidar data replayed
            timestamp = data["agent_data"][agent_ID]["timestamp"]
            agent_state = data["agent_data"][agent_ID]["pose"]
            sensor_data = data["agent_data"][agent_ID]["sensor_data"]["lidar"]
            calibration = sensor_data.calibration
            platform = calibration.reference

            # run agent pipeline
            self.agents[agent_ID].pipeline(
                timestamp=timestamp,
                agent_state=agent_state,
                sensor_data=sensor_data,
                platform=platform,
                calibration=calibration,
            )

            # store necessary data
            agent_platforms[agent_ID] = self.agents[agent_ID].pose.as_reference()
            agent_fovs_global[agent_ID] = self.agents[agent_ID].get_fov_global()
            agent_dets_global[agent_ID] = self.agents[agent_ID].get_detections_global()
            agent_tracks_global[agent_ID] = self.agents[agent_ID].get_tracks_global()

        # predict command center tracks
        timestamp = self.t0 + data["timestamp_dt"]
        cc_tracks_global = self.command_center.predict_tracks(timestamp=timestamp)

        # run trust estimation
        self.trust_estimator(
            frame=data["frame"],
            timestamp=data["timestamp"],
            agent_poses=agent_platforms,
            agent_fovs=agent_fovs_global,
            agent_dets=agent_dets_global,
            agent_tracks=agent_tracks_global,
            cc_tracks=cc_tracks_global,
        )

        # run command center pipelines in global
        self.command_center.pipeline(
            agent_dets=agent_dets_global,
            agent_fovs=agent_fovs_global,
            agent_platforms=agent_platforms,
        )

        # save the results in stonesoup format
        agent_positions = {ID: pose.x for ID, pose in agent_platforms.items()}
        data_output = {
            "agent_positions": agent_positions,
            "agent_fovs_global": agent_fovs_global,
            "agent_dets_global": agent_dets_global,
            "cc_tracks_global": cc_tracks_global,
        }

        return data_output
