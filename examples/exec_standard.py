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

import avstack
import pygame
from avapi.carla import config
from avapi.carla.simulator import bootstrap


def extend_save_folder(folder_base):
    return os.path.join(
        folder_base, "run_" + datetime.now().strftime("%Y_%m_%d_%H:%M:%S")
    )


def main(args):
    print('Random seed: {}'.format(args.seed))
    random.seed(args.seed)
    if args.remove_data and os.path.exists("sim-results/"):
        print("Removing existing sensor data...", end="")
        shutil.rmtree("sim-results/")
        print("done")

    if args.version in ["0.9.10", "0.9.10.1"]:
        raise RuntimeError(
            f"Do not use version {args.version} because the sensor timing is buggy!"
        )

    traffic_manager = None
    carla_manager = None
    display_manager = None
    keyboard_control = None
    clock = None
    cfg_carla = config.read_config(args.config_carla)

    # Main loop
    started = False
    try:
        # -- avstack inits
        ego_stack = avstack.ego.get_ego("vehicle", args.config_avstack)

        # -- carla inits
        client, world, traffic_manager, orig_settings = bootstrap.bootstrap_client(
            cfg_carla.get("client", None)
        )
        carla_manager = bootstrap.bootstrap_standard(
            world,
            traffic_manager,
            ego_stack,
            cfg_carla,
            extend_save_folder(args.save_folder),
        )
        if not args.no_display:
            display_manager, keyboard_control = bootstrap.bootstrap_display(
                world, carla_manager.ego, cfg_carla.get("display"), None
            )

        if display_manager is not None:
            clock = pygame.time.Clock()
            world.on_tick(display_manager.hud.on_world_tick)
            if args.view == "standard":
                pass
            elif args.view == "front":
                display_manager.toggle_camera()

        # -- run loop
        world.tick()
        time.sleep(1)  # wait for settling
        i_repeats_done = 0
        t_last = time.time()
        i_frames = 0
        time_deltas = deque(maxlen=10)
        print("\n")

        # -- print display information
        if display_manager is not None:
            display_manager.print_init()
        while True:
            # -- tick the simulator
            if (keyboard_control is not None) and (
                keyboard_control.parse_events(world)
            ):
                break
            # clock.tick_busy_loop()
            world.tick()
            done, debug = carla_manager.tick()
            if (args.max_scenario_len is not None) and (
                carla_manager.t_elapsed > args.max_scenario_len
            ):
                done = True
            if done:
                i_repeats_done += 1
                if cfg_carla["ego"]["respawn_on_done"]:
                    if i_repeats_done < args.n_scenarios:
                        print("\ndone...restarting for a new run!")
                        time.sleep(5)
                        time_deltas.clear()
                        i_frames = 0
                        carla_manager.restart(
                            save_folder=extend_save_folder(args.save_folder)
                        )
                        if display_manager is not None:
                            display_manager.restart(carla_manager.ego)
                        print("\n")
                    else:
                        print("done running scenarios!")
                        break
                else:
                    print("done!")
                    break
            if display_manager is not None:
                display_manager.tick(world, carla_manager.ego, clock, debug=debug)
                display_manager.render()

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
    finally:
        if started:
            if carla_manager.recorder is not None:
                print(
                    f"Waiting {args.image_dump_time} sec to allow images to dump...",
                    end="",
                    flush=True,
                )
                try:
                    time.sleep(args.image_dump_time)
                except KeyboardInterrupt:
                    pass  # allow keyboard override
        print("Done! Cleaning up...")
        print("\n")
        if display_manager is not None:
            print("Destorying display manager")
            display_manager.destroy()
        if carla_manager is not None:
            print("Destorying carla manager")
            carla_manager.destroy()
        print("Finished cleanup!")


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--config_carla", required=True
    )  # default='scenarios/parallel_park.yml'
    argparser.add_argument(
        "--config_avstack", default="Level2GroundTruthPerception", required=True
    )
    argparser.add_argument("--save_folder", default="sim-results", type=str)
    argparser.add_argument("--seed", default=None, type=int)
    argparser.add_argument("--view", default="standard", choices=["standard", "front"])
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
        "--n_scenarios", default=None, type=int, help="Number of scenarios for repeats"
    )
    argparser.add_argument(
        "--max_scenario_len", default=None, type=float, help="Time length of scenarios"
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
