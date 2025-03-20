import argparse
import json
import os
import shutil

from avapi.carla import CarlaScenesManager
from tqdm import tqdm


def main(args):
    """Convert Carla dataset to the COCO format"""

    # make dir structure
    if os.path.exists(args.output_dir):
        shutil.rmtree(args.output_dir)
    img_dir = os.path.join(args.output_dir, "images")
    ann_dir = os.path.join(args.output_dir, "annotations")
    os.makedirs(img_dir)
    os.makedirs(ann_dir)

    # set up categories
    category_ids = {
        "person": 0,
        "car": 1,
        "motorcycle": 2,
        "bicycle": 3,
        "truck": 4,
    }
    supercategories = {
        "person": "person",
        "car": "vehicle",
        "motorcycle": "vehicle",
        "bicycle": "bicycle",
        "truck": "vehicle",
    }
    categories = [
        {
            "id": v,
            "name": k,
            "supercategory": supercategories[k],
        }
        for k, v in category_ids.items()
    ]

    # loop over the splits
    idx_img = 0
    idx_ann = 0
    CSM = CarlaScenesManager(args.input_dir)
    for split, scenes in CSM.splits_scenes.items():
        os.makedirs(os.path.join(img_dir, split))
        images = []
        annotations = []

        # loop over scenes
        for idx_scene, scene in enumerate(scenes):
            # get dataset manager
            CDM = CSM.get_scene_dataset_by_name(scene)

            # loop over agents and cameras
            agents = CDM.agent_IDs
            for idx_agent, agent in enumerate(agents):
                for sensor in CDM.sensor_IDs[agent]:
                    if "camera" in sensor:
                        # parse the camera type
                        is_depth = "depth" in sensor.lower()
                        is_semseg = "semseg" in sensor.lower()
                        is_rgb = (not is_depth) and (not is_semseg)
                        if (
                            (args.use_rgb and is_rgb)
                            or (args.use_depth and is_depth)
                            or (args.use_semseg and is_semseg)
                        ):
                            # run the processing
                            print(
                                f"Processing scene {idx_scene+1}/{len(scenes)}, agent {idx_agent+1}/{len(agents)}, {sensor}"
                            )
                            frames = CDM.get_frames(sensor=sensor, agent=agent)[
                                args.idx_frame_start :: args.stride
                            ]
                            for idx_frame, frame in tqdm(
                                enumerate(frames), total=len(frames)
                            ):
                                # get gt data
                                img_filepath = CDM.get_sensor_data_filepath(
                                    frame=frame, sensor=sensor, agent=agent
                                )
                                objs = CDM.get_objects(
                                    frame=frame, sensor=sensor, agent=agent
                                )
                                calib = CDM.get_calibration(
                                    frame=frame, sensor=sensor, agent=agent
                                )

                                # symbolic link to image
                                img_filename = img_filepath.split("/")[-1]
                                src_img = img_filepath
                                dst_img = os.path.join(
                                    img_dir,
                                    split,
                                    f"scene-{idx_scene}-agent-{agent}-{sensor}-{img_filename}",
                                )
                                os.symlink(src_img, dst_img)
                                images.append(
                                    {
                                        "id": idx_img,
                                        "width": calib.img_shape[1],
                                        "height": calib.img_shape[0],
                                        "file_name": dst_img,
                                        "scene": scene,
                                        "frame": frame,
                                        "idx_frame": (idx_frame * args.stride)
                                        + args.idx_frame_start,
                                        "sensor": sensor,
                                        "agent": agent,
                                    }
                                )

                                # add annotation information
                                for obj in objs:
                                    # pull off boes
                                    box_3d = obj.box
                                    box_2d = box_3d.project_to_2d_bbox(calib=calib)

                                    # compute additional attributes
                                    volume_3d = box_3d.volume
                                    orientation_3d = box_3d.yaw
                                    fraction_visible = obj.visible_fraction
                                    if fraction_visible is None:
                                        fraction_visible = 1.0  # TODO

                                    # store annotation details
                                    annotations.append(
                                        {
                                            "id": idx_ann,
                                            "category_id": category_ids[obj.obj_type],
                                            "iscrowd": 0,
                                            "segmentation": [
                                                []
                                            ],  # TODO: segmentation mask
                                            "area": 1000,  # TODO: segmentation area
                                            "volume_3d": volume_3d,
                                            "orientation_3d": orientation_3d,
                                            "fraction_visible": fraction_visible,
                                            "image_id": idx_img,
                                            "bbox": box_2d.box2d_xywh,
                                        }
                                    )
                                    idx_ann += 1
                                idx_img += 1

        # package up the annotations
        annotation_data = {
            "images": images,
            "annotations": annotations,
            "categories": categories,
        }

        # save the annotations for this split
        ann_file = os.path.join(ann_dir, f"{split}.json")
        with open(ann_file, "w") as f:
            json.dump(annotation_data, f)
        print(f"Saved {ann_file} file")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dir", default="/data/shared/CARLA/dataset/raw", type=str
    )
    parser.add_argument(
        "--output_dir", default="/data/shared/CARLA/dataset/coco", type=str
    )
    parser.add_argument("--stride", default=4, type=int)
    parser.add_argument("--idx_frame_start", default=1, type=int)
    parser.add_argument(
        "--use_rgb", action="store_true", help="Enable if you want RGB images"
    )
    parser.add_argument(
        "--use_depth", action="store_true", help="Enable if you want depth images"
    )
    parser.add_argument(
        "--use_semseg",
        action="store_true",
        help="Enable if you want semantic segmentation images",
    )

    args = parser.parse_args()
    main(args)
