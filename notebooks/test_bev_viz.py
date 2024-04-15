import cProfile
import os

from avapi.carla import CarlaScenesManager
from avapi.visualize.snapshot import show_lidar_bev_with_boxes
from tqdm import tqdm


def main():
    cpath = os.path.join("/data/shared/CARLA/multi-agent-v1/")
    CSM = CarlaScenesManager(cpath)
    CDM = CSM.get_scene_dataset_by_name(CSM.splits_scenes["val"][0])

    frame = 12

    pc = CDM.get_lidar(sensor="lidar-0", agent=0, frame=frame)
    objs = CDM.get_objects(sensor="lidar-0", agent=0, frame=frame)

    for _ in tqdm(range(100)):
        _ = show_lidar_bev_with_boxes(pc=pc, boxes=objs, show=False, return_image=True)


if __name__ == "__main__":
    pr = cProfile.Profile()
    pr.enable()
    main()
    pr.disable()
    pr.dump_stats("bev_viz.prof")
