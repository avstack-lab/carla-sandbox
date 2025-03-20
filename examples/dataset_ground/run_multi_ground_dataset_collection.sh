#!/usr/bin/env bash

set -e

NRUNS=${1:-5}
I_SEED_START=${2:-10}

for i in $(seq 1 $NRUNS); do 
    let seed=i+$I_SEED_START
    printf "RUN {${i}}/{${NRUNS}} WITH SEED {${seed}}\n\n"
    ./run_egtr_dataset_collection.sh v1 $seed;
done
