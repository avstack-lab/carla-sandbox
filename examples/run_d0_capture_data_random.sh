#!/usr/bin/env bash

N_SCENARIOS=${1:-20}
MAX_SCENARIO_LEN=${2:-2}

python exec_standard.py \
	--n_scenarios $N_SCENARIOS \
	--max_scenario_len $MAX_SCENARIO_LEN \
	--config_avstack 'PassthroughAutopilotVehicle' \
	--config_carla 'scenarios/data_capture.yml' \
	--image_dump_time 25 \
	--seed 1