import datetime
import os


_save_folder = "sim_results/run-{date:%Y-%m-%d_%H:%M:%S}".format(
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
            "location": [0, 0, 50],
            "rotation": [0, 90, 0],
            "camera": True,
        },
        "post_hooks": [_sensor_data_logger],
    },
]
_empty_pipeline = {"type": "SerialPipeline", "modules": []}

actor_manager = {
    "type": "CarlaObjectManager",
    "subname": "actors",
    "objects": [
        {
            "type": "CarlaStaticActor",
            "spawn": 1,
            "sensors": _infra_sensor_suite,
            "pipeline": _empty_pipeline,
        },
        {
            "type": "CarlaStaticActor",
            "spawn": 2,
            "sensors": _infra_sensor_suite,
            "pipeline": _empty_pipeline,
        },
        {
            "type": "CarlaStaticActor",
            "spawn": 3,
            "sensors": _infra_sensor_suite,
            "pipeline": _empty_pipeline,
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
