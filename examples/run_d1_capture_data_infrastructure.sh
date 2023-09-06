#!/usr/bin/env bash

N_SCENARIOS=${1:-20}
MAX_SCENARIO_LEN=${2:-20}

source setup_for_standard.bash

python exec_standard.py \
    --n_scenarios $N_SCENARIOS \
    --max_scenario_len $MAX_SCENARIO_LEN \
    --config_avstack 'PassthroughAutopilotVehicle' \
    --config_carla 'scenarios/collaborative_capture_data.yml' \
    --image_dump_time 25 \
    --seed 1