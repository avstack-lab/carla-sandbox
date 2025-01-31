#!/usr/bin/env bash

set -e

IN_DIR=${1:-"/data/shared/CARLA/multi-agent-aerial-dense/raw"}
OUT_DIR=${2:-"/data/shared/CARLA/multi-agent-aerial-dense/coco"}
STRIDE=${3:-4}


python carla_to_coco.py \
    --input_dir $IN_DIR \
    --output_dir $OUT_DIR \
    --stride $STRIDE \
    --use_rgbdata-timest