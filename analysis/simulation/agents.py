import os
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from datetime import datetime
    from avstack.config import ConfigDict


from avstack.config import AGENTS, MODELS
from avstack.geometry import GlobalOrigin3D
from avstack.utils.logging import StoneSoupTracksLogger


class Agent:
    def __init__(
        self,
        ID: int,
        t_start: "datetime",
        localization: "ConfigDict",
        fov_estimator: "ConfigDict",
        perception: "ConfigDict",
        tracking: "ConfigDict",
        log_dir: str,
        log_fov: bool = True,
        log_local: bool = True,
        log_percep: bool = True,
        log_track: bool = False,
    ):
        self.ID = ID
        self.t_start = t_start
        self.log_dir = log_dir

        # add logging hooks
        out_folder = os.path.join(log_dir, f"agent-{ID}", "{}")
        if log_local:
            localization["post_hooks"] = [
                {
                    "type": "AgentPoseLogger",
                    "output_folder": out_folder.format("pose"),
                }
            ]
        if log_fov:
            fov_estimator["post_hooks"] = [
                {
                    "type": "FieldOfViewLogger",
                    "output_folder": out_folder.format("fov"),
                }
            ]
        if log_percep:
            perception["post_hooks"] = [
                {
                    "type": "DetectionsLogger",
                    "output_folder": out_folder.format("detections"),
                }
            ]
        if log_track:
            tracking["post_hooks"] = [
                {
                    "type": "StoneSoupTracksLogger",
                    "output_folder": out_folder.format("tracks"),
                }
            ]

        # build models
        self.fov_estimator = MODELS.build(fov_estimator)
        self.localization = MODELS.build(localization, default_args={"t_init": t_start})
        self.perception = MODELS.build(perception)
        self.tracking = MODELS.build(tracking, default_args={"t0": t_start})

        # presets
        self.reference = None
        self.fov = None
        self.detections = []
        self.tracks = []

    def pipeline(self, timestamp, sensor_data, agent_state, platform, calibration):
        self.reference = platform
        self.pose = self.localization(timestamp, agent_state)
        self.fov = self.fov_estimator(sensor_data, in_global=False)
        self.detections = self.perception(sensor_data)
        self.tracks = self.tracking(
            self.detections, platform=platform, calibration=calibration
        )

    def get_detections_global(self):
        dets_global = self.detections.apply_and_return(
            "change_reference", GlobalOrigin3D, inplace=False
        )
        return dets_global

    def get_fov_global(self):
        if self.fov is not None:
            fov_global = self.fov.change_reference(GlobalOrigin3D, inplace=False)
        else:
            raise RuntimeError("FOV is not properly set yet")
        return fov_global

    def get_tracks_global(self):
        boxes = self.tracks.apply_and_return("getattr", "box3d")
        tracks_global = boxes.apply_and_return(
            "change_reference", GlobalOrigin3D, inplace=False
        )
        return tracks_global

    def shutdown(self):
        # save the stone soup tracks only on shutdown
        out_folder = os.path.join(self.log_dir, f"agent-{self.ID}", "tracks")
        StoneSoupTracksLogger(output_folder=out_folder)(self.tracks)


@AGENTS.register_module()
class MobileAgent(Agent):
    def __init__(
        self,
        ID: int,
        t_start: "datetime",
        localization: "ConfigDict" = {"type": "GroundTruthLocalizer"},
        fov_estimator: "ConfigDict" = {"type": "ConcaveHullLidarFOVEstimator"},
        perception: "ConfigDict" = {
            "type": "MMDetObjectDetector3D",
            "model": "pointpillars",
            "dataset": "carla-vehicle",
            "gpu": 0,
            "thresh_duplicate": 1.0,
        },
        tracking: "ConfigDict" = {
            "type": "StoneSoupKalmanTracker3DBox",
        },
        log_dir: str = "last_run",
    ):
        super().__init__(
            ID, t_start, localization, fov_estimator, perception, tracking, log_dir
        )


@AGENTS.register_module()
class StaticAgent(Agent):
    def __init__(
        self,
        ID: int,
        t_start: "datetime",
        localization: "ConfigDict" = {"type": "GroundTruthLocalizer"},
        fov_estimator: "ConfigDict" = {"type": "ConcaveHullLidarFOVEstimator"},
        perception: "ConfigDict" = {
            "type": "MMDetObjectDetector3D",
            "model": "pointpillars",
            "dataset": "carla-infrastructure",
            "gpu": 0,
            "thresh_duplicate": 1.0,
        },
        tracking: "ConfigDict" = {
            "type": "StoneSoupKalmanTracker3DBox",
        },
        log_dir: str = "last_run",
    ):
        super().__init__(
            ID, t_start, localization, fov_estimator, perception, tracking, log_dir
        )


@AGENTS.register_module()
class CommandCenter:
    def __init__(
        self,
        t_start: "datetime",
        tracking: "ConfigDict" = {
            "type": "MeasurementBasedMultiTracker",
            "tracker": {"type": "BasicBoxTracker3D"},
            # "tracker": {"type": "StoneSoupKalmanTracker3DBox"},
        },
        log_dir: str = "last_run",
        log_track: bool = True,
    ):
        self.log_dir = log_dir
        self.tracks = None
        self._log_soup = False

        # add logging hooks
        if log_track:
            out_folder = os.path.join(log_dir, f"command-center", "{}")
            if "StoneSoup" not in tracking["tracker"]["type"]:
                tracking["post_hooks"] = [
                    {
                        "type": "TracksLogger",
                        "output_folder": out_folder.format("tracks"),
                    }
                ]
            else:
                self._log_soup = True

        # build models
        tracking["tracker"]["t0"] = t_start
        self.tracking = MODELS.build(tracking)

    def pipeline(self, agent_dets, agent_fovs, agent_platforms):
        """Run the command center pipeline

        NOTE: all input data are in global coordinates
        """
        self.tracks = self.tracking(
            detections=agent_dets, fovs=agent_fovs, platforms=agent_platforms
        )

    def predict_tracks(self, timestamp: "datetime"):
        tracks_predicted = self.tracking.predict_tracks(
            timestamp, platform=GlobalOrigin3D, check_reference=False
        )
        return tracks_predicted

    def shutdown(self):
        # save the stone soup tracks only on shutdown
        if self._log_soup:
            out_folder = os.path.join(self.log_dir, f"command-center", "tracks")
            StoneSoupTracksLogger(output_folder=out_folder)(self.tracks)
