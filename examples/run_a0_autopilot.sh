#!/usr/bin/env bash

source setup_for_standard.bash

python exec_standard.py \
    --config_manager 'config/manager/default.py' \
    --config_world 'config/world/default_world.py' \
    --seed 1 \
    --remove_data