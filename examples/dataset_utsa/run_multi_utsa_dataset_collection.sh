#!/usr/bin/env bash

set -e

NRUNS=${1:-10}
I_SEED_START=${2:-1}
VERSION=${3-v1}

for i in $(seq 1 $NRUNS); do 
    let seed=i+$I_SEED_START
    printf "RUN {${i}}/{${NRUNS}} WITH SEED {${seed}}\n\n"
    ./run_utsa_dataset_collection.sh $VERSION $seed;
done
