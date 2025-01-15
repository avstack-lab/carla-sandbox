_sensor_data_logger = {
    "type": "SensorDataLogger",
    "output_folder": "sim_results/__OUTPUT_FOLDER__/data",
}

_object_data_logger = {
    "type": "ObjectStateLogger",
    "output_folder": "sim_results/__OUTPUT_FOLDER__/objects",
}

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

n_actors = 5
actor_manager = {
    "type": "CarlaObjectManager",
    "subname": "actors",
    "objects": [
        {
            "type": "CarlaMobileActor",
            "spawn": "random",
            "vehicle": 1,
            "destination": None,
            "autopilot": True,
            "sensors": _mobile_sensor_suite,
            "pipeline": _empty_pipeline,
        }
        for idx_actor in range(n_actors)
    ],
    "post_hooks": [_object_data_logger],
}

_n_npcs = 100
npc_manager = {
    "type": "CarlaObjectManager",
    "subname": "npcs",
    "objects": [
        *[
            {"type": "CarlaNpc", "spawn": "random", "npc_type": "vehicle"}
            for _ in range(_n_npcs)
        ],
    ],
    "post_hooks": [_object_data_logger],
}
