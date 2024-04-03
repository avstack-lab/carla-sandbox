import datetime
import os


_save_folder = "sim_results/run-{date:%Y-%m-%d_%H:%M:%S}-intersection".format(
    date=datetime.datetime.now()
)
_sensor_data_logger = {
    "type": "SensorDataLogger",
    "output_folder": os.path.join(_save_folder, "data"),
}
_object_data_logger = {
    "type": "ObjectStateLogger",
    "output_folder": os.path.join(_save_folder, "objects"),
}
_infra_sensor_suite = [
    {
        "type": "CarlaRgbCamera",
        "name": "camera-0",
        "reference": {
            "type": "CarlaReferenceFrame",
            "camera": True,
        },
        "post_hooks": [_sensor_data_logger],
    },
    {
        "type": "CarlaLidar",
        "name": "lidar-0",
        "horizontal_fov": 120.0,
        "upper_fov": 30.0,
        "lower_fov": -30.0,
        "channels": 64,
        "points_per_second": 2240000,  # 1750 * 64 * 60 * 120/360
        "reference": {
            "type": "CarlaReferenceFrame",
            "camera": False,
        },
        "post_hooks": [_sensor_data_logger],
    },
]
_mobile_sensor_suite = [
    {
        "type": "CarlaRgbCamera",
        "name": "camera-0",
        "post_hooks": [_sensor_data_logger],
    },
    {
        "type": "CarlaRgbCamera",
        "name": "camera-1",
        "reference": {
            "type": "CarlaReferenceFrame",
            "location": [-1.5, 0, 1.6],
            "rotation": [0, 0, 180],
            "camera": True,
        },
        "post_hooks": [_sensor_data_logger],
    },
    {
        "type": "CarlaLidar",
        "name": "lidar-0",
        "post_hooks": [_sensor_data_logger],
    },
    {
        "type": "CarlaGnss",
        "name": "gnss-0",
        "post_hooks": [_sensor_data_logger],
    },
    {
        "type": "CarlaImu",
        "name": "imu-0",
        "post_hooks": [_sensor_data_logger],
    },
]
_empty_pipeline = {"type": "SerialPipeline", "modules": []}

actor_manager = {
    "type": "CarlaObjectManager",
    "subname": "actors",
    "objects": [
        {
            "type": "CarlaMobileActor",
            "spawn": 1,
            "reference_to_spawn": {
                "type": "CarlaReferenceFrame",
                "location": [-20, 0, 0],
                "camera": False,
            },
            "vehicle": 1,
            "destination": None,
            "autopilot": True,
            "sensors": _mobile_sensor_suite,
            "pipeline": _empty_pipeline,
        },
        {
            "type": "CarlaStaticActor",
            "spawn": 1,
            "sensors": _infra_sensor_suite,
            "pipeline": _empty_pipeline,
            "reference_to_spawn": {
                "type": "CarlaReferenceFrame",
                "location": [0, 0, 20],
                "rotation": [0, 30, 0],
                "camera": False,
            }
        },
        {
            "type": "CarlaStaticActor",
            "spawn": 1,
            "sensors": _infra_sensor_suite,
            "pipeline": _empty_pipeline,
            "reference_to_spawn": {
                "type": "CarlaReferenceFrame",
                "location": [16, -22, 20],
                "rotation": [0, 30, 90],
                "camera": False,
            }
        },
        {
            "type": "CarlaStaticActor",
            "spawn": 1,
            "sensors": _infra_sensor_suite,
            "pipeline": _empty_pipeline,
            "reference_to_spawn": {
                "type": "CarlaReferenceFrame",
                "location": [16, 30, 20],
                "rotation": [0, 30, -90],
                "camera": False,
            }
        },
        
    ],
    "post_hooks": [_object_data_logger],
}

_n_npcs = 50
npc_manager = {
    "type": "CarlaObjectManager",
    "subname": "npcs",
    "objects": [
        {"type": "CarlaNpc", "spawn": "random", "npc_type": "vehicle"}
        for _ in range(_n_npcs)
    ],
    "post_hooks": [_object_data_logger],
}
