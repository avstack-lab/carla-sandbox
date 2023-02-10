#!/usr/bin/env bash

source setup_for_standard.bash

python exec_standard.py \
    --config_avstack 'PassthroughAutopilotVehicle' \
    --config_carla 'scenarios/base_autopilot.yml' \
    --seed 1 \
    --remove_data