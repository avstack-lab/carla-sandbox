# -*- coding: utf-8 -*-
# @Author: Spencer H
# @Date:   2022-03-20
# @Last Modified by:   Spencer H
# @Last Modified date: 2022-10-22
# @Description:
"""
Run a standard scenario from config file
"""


import argparse
import cProfile
import logging
import os
import random
import shutil
import time
from collections import deque
from datetime import datetime

import pygame
from avcarla import CARLA
from avstack.config import Config


def extend_save_folder(folder_base):
    return os.path.join(
        folder_base, "run_" + datetime.now().strftime("%Y_%m_%d_%H:%M:%S")
    )


def main(args):
    print("Random seed: {}".format(args.seed))
    random.seed(args.seed)
    if args.remove_data and os.path.exists(args.save_folder):
        print("Removing existing sensor data...", end="")
        shutil.rmtree(args.save_folder)
        print("done")

    if args.version in ["0.9.10", "0.9.10.1"]:
        raise RuntimeError(
            f"Do not use version {args.version} because the sensor timing is buggy!"
        )

    client = None
    display = None
    actor_manager = None
    npc_manager = None
    clock = None

    cfg_manager = Config.fromfile(args.config_manager)
    cfg_world = Config.fromfile(args.config_world)

    # Main loop
    try:
        # -- initializations
        client = CARLA.build(cfg_world["client"])
        actor_manager = CARLA.build(
            cfg_manager["actor_manager"], default_args={"client": client}
        )
        npc_manager = CARLA.build(
            cfg_manager["npc_manager"], default_args={"client": client}
        )
        client.on_tick(actor_manager.on_world_tick)
        client.on_tick(npc_manager.on_world_tick)

        if not args.no_display:
            display = CARLA.build(
                cfg_world["display"],
                default_args={"client": client, "manager": actor_manager},
            )
            clock = pygame.time.Clock()

        # -- run loop
        time.sleep(1)  # wait for settling
        i_repeats_done = 0
        t_last = time.time()
        i_frames = 0
        time_deltas = deque(maxlen=10)
        started = False
        print("\n")

        # -- print display information
        if display is not None:
            display.print_init()
        while True:
            # -- initialize on first
            if not started:
                snap = client.world.get_snapshot()
                frame0 = snap.frame
                t0 = snap.timestamp.elapsed_seconds
                actor_manager.initialize(t0=t0, frame0=frame0)
                npc_manager.initialize(t0=t0, frame0=frame0)

            # -- parse keyboard controls
            if (
                (display is not None)
                and (display.keyboard_control is not None)
                and (display.keyboard_control.parse_events(client.world))
            ):
                break

            # -- tick the client
            client.tick()

            # -- update display (for not only using ego...eventually all actors)
            debug = {
                "ground_truth": {"objects": {}},
                "actors": [{"objects": {}} for _ in actor_manager.objects],
            }
            if display is not None:
                clock.tick_busy_loop()
                display.tick(client=client, clock=clock, debug=debug)
                display.render()

            # -- print execution rate
            i_frames += 1
            t_now = time.time()
            time_deltas.append(t_now - t_last)
            if i_frames > 3:
                fps = len(time_deltas) / sum(time_deltas)
                print(
                    "Exec. rate: %.4f FPS, %04i frames" % (fps, i_frames),
                    end="\r",
                    flush=True,
                )
            t_last = t_now
            started = True
    except (KeyboardInterrupt, Exception) as e:
        print("")
        if args.hard_fail:
            raise e
        else:
            logging.warning(e, exc_info=True)
    else:
        print("Done naturally")
    finally:
        # wait before destroy
        try:
            if args.image_dump_time:
                print("waiting to allow images to dump...")
                for i in range(int(args.image_dump_time), 0, -1):
                    print(f"{i:02d}", end="\r", flush=True)
                    time.sleep(1)
        except KeyboardInterrupt:
            pass

        # destroy display and actors
        if display is not None:
            print("Destorying display")
            display.destroy()
        if actor_manager is not None:
            print("Destorying actor manager")
            actor_manager.destroy()
        if npc_manager is not None:
            print("Destroying npc manager")
            npc_manager.destroy()
        print("Finished cleanup!")


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--config_world", required=True)
    argparser.add_argument("--config_manager", required=True)
    argparser.add_argument("--save_folder", default="sim-results", type=str)
    argparser.add_argument("--seed", default=None, type=int)
    argparser.add_argument(
        "--version",
        default="0.9.13",
        choices=["0.9.10", "0.9.10.1", "0.9.11", "0.9.12", "0.9.13"],
    )
    argparser.add_argument("--remove_data", action="store_true")
    argparser.add_argument(
        "--image_dump_time", default=10, type=int, help="Time to allow images to dump"
    )
    argparser.add_argument(
        "--hard_fail", action="store_true", help="Enable to hard fail with an error"
    )
    argparser.add_argument(
        "--no_display", action="store_true", help="Add flag to disable display"
    )
    args = argparser.parse_args()

    pr = cProfile.Profile()
    pr.enable()
    main(args)
    pr.disable()
    pr.dump_stats("last_run.prof")
