#!/usr/bin/env bash

source ../setup_for_standard.bash

python ../exec_standard.py \
    --config_manager 'config/dataset_collection.py' \
    --config_world '../config/world/default_world.py' \
    --duration 20 \
    --remove_data
