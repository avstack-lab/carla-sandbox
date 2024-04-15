import os

import numpy as np
from avapi.visualize.movie import make_movie
from avstack.calibration import LidarCalibration
from avstack.geometry import GlobalOrigin3D, PointMatrix3D
from avstack.sensors import LidarData


def make_agent_movies(
    imgs,
    pcs,
    dets,
    tracks,
    agent,
    vid_folder="videos",
    percep_movies=True,
    track_movies=True,
    img_movies=True,
    bev_movies=True,
    extent=None,
):
    os.makedirs(vid_folder, exist_ok=True)

    ###############################################
    # CAMERA-BASED VISUALIZATION
    ###############################################
    # perception movie
    if percep_movies and img_movies:
        make_movie(
            raw_imgs=imgs,
            raw_pcs=pcs,
            boxes=dets,
            name=os.path.join(vid_folder, f"agent-{agent}-perception-img"),
            save=True,
            show_in_notebook=False,
            projection="img",
            extent=extent,
        )

    # tracking movie
    if track_movies and img_movies:
        make_movie(
            raw_imgs=imgs,
            raw_pcs=pcs,
            boxes=tracks,
            name=os.path.join(vid_folder, f"agent-{agent}-tracking-img"),
            save=True,
            show_in_notebook=False,
            projection="img",
            extent=extent,
        )

    ###############################################
    # BEV-BASED VISUALIZATION
    ###############################################
    # perception movie
    if percep_movies and bev_movies:
        make_movie(
            raw_imgs=imgs,
            raw_pcs=pcs,
            boxes=dets,
            name=os.path.join(vid_folder, f"agent-{agent}-perception-bev"),
            save=True,
            show_in_notebook=False,
            projection="bev",
            extent=extent,
        )

    # tracking movie
    if track_movies and bev_movies:
        make_movie(
            raw_imgs=imgs,
            raw_pcs=pcs,
            boxes=tracks,
            name=os.path.join(vid_folder, f"agent-{agent}-tracking-bev"),
            save=True,
            show_in_notebook=False,
            projection="bev",
            extent=extent,
        )


def make_central_movie(pcs_all, tracks, extent=None, vid_folder="videos"):
    os.makedirs(vid_folder, exist_ok=True)

    # aggregate all point clouds in global frame
    calib_global = LidarCalibration(GlobalOrigin3D)
    pc_data = [[] for _ in range(len(list(pcs_all.values())[0]))]
    for agent, pcs_agent in pcs_all.items():
        for frame, pc in enumerate(pcs_agent):
            pc = pc.project(calib_global)
            pc_data[frame].append(pc.data.x)
    pcs = []
    for i in range(len(pc_data)):
        pc_data[i] = PointMatrix3D(
            x=np.concatenate(pc_data[i], axis=0), calibration=calib_global
        )
        pcs.append(
            LidarData(
                data=pc_data[i],
                timestamp=0,
                frame=i,
                source_name="lidar",
                source_ID=0,
                calibration=calib_global,
            )
        )

    # tracking movie
    make_movie(
        raw_imgs=[[]] * len(pcs),
        raw_pcs=pcs,
        boxes=tracks,
        name=os.path.join(vid_folder, f"central-tracking-bev"),
        save=True,
        show_in_notebook=False,
        projection="bev",
        extent=extent,
    )
