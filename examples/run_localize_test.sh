#!/usr/bin/env bash

SCENARIO=$1

source setup_for_standard.bash

python exec_standard.py \
	--config_avstack 'Level2GroundTruthPerception' \
 	--config_carla scenarios/follow_"$SCENARIO".yml \
	--seed 1 \
	--remove_data \
	--hard_fail
