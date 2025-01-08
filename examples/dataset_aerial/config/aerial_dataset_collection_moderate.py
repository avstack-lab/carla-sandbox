_sensor_data_logger = {
    "type": "SensorDataLogger",
    "output_folder": "sim_results/__OUTPUT_FOLDER__/data",
}

_object_data_logger = {
    "type": "ObjectStateLogger",
    "output_folder": "sim_results/__OUTPUT_FOLDER__/objects",
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
        "type": "CarlaDepthCamera",
        "name": "depthcamera-0",
        "reference": {
            "type": "CarlaReferenceFrame",
            "camera": True,
        },
        "post_hooks": [_sensor_data_logger],
    },
]
_empty_pipeline = {"type": "SerialPipeline", "modules": []}

_n_actors = 10
actor_manager = {
    "type": "CarlaObjectManager",
    "subname": "actors",
    "objects": [
        {
            "type": "CarlaStaticActor",
            "spawn": "random",
            "reference_to_spawn": {
                "type": "CarlaReferenceFrame",
                "location": [0, 0, 50],
                "rotation": [0, 90, 0],
                "camera": False,
            },
            "sensors": _infra_sensor_suite,
            "pipeline": _empty_pipeline,
        }
        for _ in range(_n_actors)
    ],
    "post_hooks": [_object_data_logger],
}

_n_npcs = 50
npc_manager = {
    "type": "CarlaObjectManager",
    "subname": "npcs",
    "objects": [
        {"type": "CarlaNpc", "spawn": "random", "npc_type": "random-vehicle"}
        for _ in range(_n_npcs)
    ],
    "post_hooks": [_object_data_logger],
}
