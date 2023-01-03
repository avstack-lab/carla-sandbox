#!/usr/bin/env bash

source setup_for_standard.bash

python exec_standard.py \
    --config_avstack 'GroundTruthMapPlanner' \
    --config_carla 'scenarios/roaming.yml' \
    --seed 1 \
    --remove_data
