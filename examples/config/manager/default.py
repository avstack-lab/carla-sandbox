_infra_sensor_suite = [
    {
        "type": "CarlaRgbCamera",
        "name": "camera-0",
        "reference": {
            "type": "CarlaReferenceFrame",
            "location": [0, 0, 15],
            "rotation": [0, 20, 0],
            "camera": True,
        },
    },
]
_mobile_sensor_suite = [
    {
        "type": "CarlaRgbCamera",
        "name": "camera-0",
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
    },
    {
        "type": "CarlaLidar",
        "name": "lidar-0",
    },
    {
        "type": "CarlaGnss",
        "name": "gnss-0",
    },
    {
        "type": "CarlaImu",
        "name": "imu-0",
    },
]
_empty_pipeline = {"type": "SerialPipeline", "modules": []}
# _image_pipeline = {
#     "type": "SerialPipeline",
#     "modules": [
#         {
#             "type": "CarlaImageDetector",
#             "pre_hooks": [],
#             "algorithm": {"type": "MMDetObjectDetector2D", "pre_hooks": []},
#         }
#     ],
# }

actor_manager = {
    "type": "CarlaObjectManager",
    "subname": "actors",
    "objects": [
        {
            "type": "CarlaMobileActor",
            "spawn": 0,
            "vehicle": 0,
            "destination": None,
            "autopilot": True,
            "sensors": _mobile_sensor_suite,
            "pipeline": _empty_pipeline,
        },
        {
            "type": "CarlaMobileActor",
            "spawn": 1,
            "vehicle": 1,
            "destination": None,
            "autopilot": True,
            "sensors": _mobile_sensor_suite,
            "pipeline": _empty_pipeline,
        },
        {
            "type": "CarlaStaticActor",
            "spawn": 2,
            "sensors": _infra_sensor_suite,
            "pipeline": _empty_pipeline,
        },
    ],
}

_n_npcs = 50
npc_manager = {
    "type": "CarlaObjectManager",
    "subname": "npcs",
    "objects": [
        {"type": "CarlaNpc", "spawn": "random", "npc_type": "vehicle"}
        for _ in range(_n_npcs)
    ],
}
