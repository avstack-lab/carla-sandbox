#!/usr/bin/env bash

source setup_for_standard.bash

python exec_standard.py \
    --config_avstack 'Level2LidarBasedVehicle' \
    --config_carla 'scenarios/base_av.yml' \
    --seed 1 \
    --remove_data