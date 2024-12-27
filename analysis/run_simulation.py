import cProfile
import json
import os
from argparse import ArgumentParser
from datetime import datetime

import avapi  # noqa # pylint: disable=unused-import; to set the registries
import avstack  # noqa # pylint: disable=unused-import; to set the registries
import mate  # noqa # pylint: disable=unused-import; to set the registries
import numpy as np
import simulation  # noqa # pylint: disable=unused-import; to set the registries
from simulation import DatasetReplayer, TrustSimulation
from tqdm import tqdm


def main(args):
    t_start = datetime(2000, 1, 1)
    agents = [
        {"type": "MobileAgent", "ID": 0, "t_start": t_start, "log_dir": args.log_dir},
        {"type": "StaticAgent", "ID": 1, "t_start": t_start, "log_dir": args.log_dir},
        {"type": "StaticAgent", "ID": 2, "t_start": t_start, "log_dir": args.log_dir},
        {"type": "StaticAgent", "ID": 3, "t_start": t_start, "log_dir": args.log_dir},
    ]
    command_center = {"type": "CommandCenter", "t_start": t_start}
    trust_estimator = {"type": "TrustEstimator"}
    simulator = TrustSimulation(
        t0=t_start,
        agents=agents,
        command_center=command_center,
        trust_estimator=trust_estimator,
        log_dir=args.log_dir,
    )
    replayer = DatasetReplayer(
        scene_index=args.scene_index, n_frames_max=args.max_frames
    )

    running = False
    all_results = []
    try:
        # run through simulator
        for data_input in tqdm(replayer(load_perception=True)):
            data_output = simulator(data_input)
            all_results.append(
                {
                    "frame": data_input["frame"],
                    "timestamp": data_input["timestamp"],
                    "timestamp_datetime": (
                        t_start + data_input["timestamp_dt"]
                    ).timestamp(),
                    "data": data_output,
                }
            )
            running = True
    except KeyboardInterrupt:
        pass
    finally:
        if running:
            # save metadata
            metadata = {"t_start": t_start.timestamp(), "replayer": replayer.metadata}
            print("Saving metadata...")
            with open(os.path.join(args.log_dir, "metadata.json"), "w") as f:
                json.dump(metadata, f)

            # save frame/timestamp information
            print("Saving frame/timestamps...")
            with open(os.path.join(args.log_dir, "timestamps.txt"), "w") as f:
                f.write(
                    "\n".join(
                        [
                            f"{res['frame']:d}, {res['timestamp_datetime']:f}"
                            for res in all_results
                        ]
                    )
                )

            # run the shutdown routine for the agents
            print("Shutting down agents...")
            for agent in [simulator.command_center, *simulator.agents.values()]:
                agent.shutdown()
            print("done.")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--scene", dest="scene_index", type=int, default=0)
    parser.add_argument("--log", dest="log_dir", type=str, default="last_run")
    parser.add_argument("--frames", dest="max_frames", type=int, default=np.inf)
    args = parser.parse_args()

    pr = cProfile.Profile()
    pr.enable()
    main(args)
    pr.disable()
    pr.dump_stats(os.path.join(args.log_dir, "last_run.prof"))
