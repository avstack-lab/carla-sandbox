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
    suffix="",
    percep_movies=True,
    track_movies=True,
    img_movies=True,
    bev_movies=True,
    extent=None,
    *args,
    **kwargs,
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
            name=os.path.join(vid_folder, f"agent-{agent}-perception-img{suffix}"),
            save=True,
            show_in_notebook=False,
            projection="img",
            extent=extent,
            *args,
            **kwargs,
        )

    # tracking movie
    if track_movies and img_movies:
        make_movie(
            raw_imgs=imgs,
            raw_pcs=pcs,
            boxes=tracks,
            name=os.path.join(vid_folder, f"agent-{agent}-tracking-img{suffix}"),
            save=True,
            show_in_notebook=False,
            projection="img",
            extent=extent,
            *args,
            **kwargs,
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
            name=os.path.join(vid_folder, f"agent-{agent}-perception-bev{suffix}"),
            save=True,
            show_in_notebook=False,
            projection="bev",
            extent=extent,
            *args,
            **kwargs,
        )

    # tracking movie
    if track_movies and bev_movies:
        make_movie(
            raw_imgs=imgs,
            raw_pcs=pcs,
            boxes=tracks,
            name=os.path.join(vid_folder, f"agent-{agent}-tracking-bev{suffix}"),
            save=True,
            show_in_notebook=False,
            projection="bev",
            extent=extent,
            *args,
            **kwargs,
        )


def make_central_movie(*args, **kwargs):
    _make_joint_movie(*args, prepend="central", **kwargs)


def make_collab_movie(*args, **kwargs):
    _make_joint_movie(*args, prepend="collab", **kwargs)


def _make_joint_movie(
    pcs_all,
    tracks,
    ego=None,
    extent=None,
    prepend="",
    vid_folder="videos",
    *args,
    **kwargs,
):
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
        x = np.concatenate(pc_data[i], axis=0)
        if ego is not None:
            ego_x = ego[i].integrate(start_at=GlobalOrigin3D).x
            rng_from_ego = np.linalg.norm(x[:, :2] - ego_x[:2], axis=1)[:, None]
            x = np.concatenate((x, rng_from_ego), axis=1)
        pc_data[i] = PointMatrix3D(x=x, calibration=calib_global)
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
        name=os.path.join(vid_folder, f"{prepend}-tracking-bev"),
        save=True,
        show_in_notebook=False,
        projection="bev",
        extent=extent,
        *args,
        **kwargs,
    )
