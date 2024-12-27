#!/usr/bin/env bash

set -e 

VERSION=${1?"Missing arg for version (e.g., v1)"}
SEED=${2:-4}
DURATION=${3:-20}

source ../setup_for_standard.bash

python ../exec_standard.py \
    --config_manager "./config/aerial_dataset_collection_${VERSION}.py" \
    --config_world "../config/world/default_world.py" \
    --seed $SEED \
    --duration $DURATION \
    --remove_data