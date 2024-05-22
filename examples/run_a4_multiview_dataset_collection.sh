#!/usr/bin/env bash

source setup_for_standard.bash

python exec_standard.py \
    --config_manager 'config/manager/multiview_dataset_collection.py' \
    --config_world 'config/world/default_world.py' \
    --seed 6 \
    --remove_data
