display = {
    "type": "CarlaDisplay",
    "enabled": True,
    "display_size": (1000, 600),
    "hud_cameras": [
        {
            "type": "CarlaRgbCamera",
            "name": "camera-hud-0",
            "image_size_x": 1000,
            "image_size_y": 600,
            "reference": {
                "type": "CarlaReferenceFrame",
                "location": [-8.5, 0, 3.5],
                "camera": True,
            },
            "do_spawn": False,
            "do_listen": False,
        },
        {
            "type": "CarlaRgbCamera",
            "name": "camera-hud-1",
            "image_size_x": 1000,
            "image_size_y": 600,
            "reference": {
                "type": "CarlaReferenceFrame",
                "location": [0, 0, 15],
                "rotation": [0, 90, 0],
                "camera": True,
            },
            "do_spawn": False,
            "do_listen": False,
        },
        {
            "type": "CarlaRgbCamera",
            "name": "camera-hud-2",
            "image_size_x": 1000,
            "image_size_y": 600,
            "reference": {
                "type": "CarlaReferenceFrame",
                "location": [-10, 5, 10],
                "rotation": [0, 45, 0],
                "camera": True,
            },
            "do_spawn": False,
            "do_listen": False,
        },
    ],
}
