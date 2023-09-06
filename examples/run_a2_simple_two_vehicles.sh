#!/usr/bin/env bash

source setup_for_standard.bash

python exec_standard.py \
    --config_avstack 'PassthroughAutopilotVehicle' \
    --config_carla 'scenarios/simple_two_vehicles.yml' \
    --seed 1 \
    --remove_data