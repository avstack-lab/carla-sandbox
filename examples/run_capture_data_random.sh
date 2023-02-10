#!/usr/bin/env bash

VERSION=${1:-0.9.13}
N_SCENARIOS=${2:-20}
MAX_SCENARIO_LEN=${3:-20}

python exec_standard.py \
  --n_scenarios $N_SCENARIOS \
  --max_scenario_len $MAX_SCENARIO_LEN \
	--config_avstack 'PassthroughAutopilotVehicle' \
	--config_carla 'scenarios/data_capture.yml' \
	--seed 1 \
	--version $VERSION
