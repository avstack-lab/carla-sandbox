from datetime import timedelta
from typing import Any

import numpy as np
from avstack.config import DATASETS, ConfigDict


@DATASETS.register_module()
class DatasetReplayer:
    def __init__(
        self,
        scene_manager: ConfigDict = {
            "type": "CarlaScenesManager",
            "data_dir": "/data/shared/CARLA/multi-agent-intersection/",
        },
        scene_index: int = 0,
        n_frames_burnin: int = 5,
        n_frames_trim: int = 2,
        n_frames_max: int = np.inf,
    ):
        # static things that stay the same
        self.scene_manager = DATASETS.build(scene_manager)
        self.scene_dataset = self.scene_manager.get_scene_dataset_by_index(scene_index)
        # HACK: fix agent and sensor to get frames
        self._default_sensor = "lidar-0"
        self._default_lidar = "lidar-0"
        self._default_camera = "camera-0"
        self._default_agent = 0
        frames = self.scene_dataset.get_frames(
            sensor=self._default_sensor, agent=self._default_agent
        )[n_frames_burnin:-n_frames_trim]
        self.frames = frames[: min(n_frames_max, len(frames))]

        # dynamic things that change
        self.index = 0

        # log metadata
        self.metadata = {
            "scene_manager": scene_manager,
            "scene_index": scene_index,
            "n_frames_burnin": n_frames_burnin,
            "n_frames_trim": n_frames_trim,
            "n_frames_max": n_frames_max,
        }

    def __getattribute__(self, __name: str) -> Any:
        try:
            # this tries to get the attribute from self
            return object.__getattribute__(self, __name)
        except AttributeError as original_error:
            if __name.startswith("_"):
                # Don't proxy special/private attributes to `state`, just raise the original error
                raise original_error
            else:
                # For non _ attributes, try to get the attribute from self.scene_dataset instead of self.
                try:
                    SD = object.__getattribute__(self, "scene_dataset")
                    return getattr(SD, __name)
                except AttributeError:
                    # If we get the error about SD not having the attribute, then we want to
                    # raise the original error instead
                    raise original_error

    def __iter__(self):
        return self

    def __next__(self):
        try:
            data = self.step()
        except IndexError:
            raise StopIteration
        return data

    def __len__(self):
        return len(self.frames)

    def __call__(self, load_perception: bool = True):
        self.load_perception = load_perception
        return self

    def step(self) -> dict:
        """Gets the next batch of data for each agent"""

        frame = self.frames[self.index]
        timestamp = self.get_timestamp(
            frame=frame, sensor=self._default_sensor, agent=self._default_agent
        )
        timestamp_dt = timedelta(seconds=timestamp)
        objects = self.get_objects_global(
            frame=frame, include_agents=True, ignore_static_agents=True
        )
        agent_data = {
            agent: {
                "frame": frame,
                "timestamp": timestamp,
                "timestamp_dt": timestamp_dt,
                "pose": self.get_agent(frame=frame, agent=agent),
                "sensor_data": {
                    "image": self.get_image(
                        frame=frame, sensor=self._default_camera, agent=agent
                    )
                    if self.load_perception
                    else None,
                    "lidar": self.get_lidar(
                        frame=frame, sensor=self._default_lidar, agent=agent
                    )
                    if self.load_perception
                    else None,
                },
                "objects": {
                    "image": self.get_objects(
                        frame=frame, sensor=self._default_camera, agent=agent
                    ),
                    "lidar": self.get_objects(
                        frame=frame, sensor=self._default_lidar, agent=agent
                    ),
                    "agent": self.get_objects(frame=frame, sensor=None, agent=agent),
                },
            }
            for agent in self.get_agent_set(frame=frame)
        }

        data = {
            "frame": frame,
            "timestamp": timestamp,
            "timestamp_dt": timestamp_dt,
            "objects": objects,
            "agent_data": agent_data,
        }

        self.index += 1

        return data

    def reset(self):
        self.index = 0
