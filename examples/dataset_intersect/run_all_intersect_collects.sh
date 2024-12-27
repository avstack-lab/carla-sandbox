#!/usr/bin/env bash

set -e

for i in {0..3}; do 
    let seed=i+3
    printf "RUN {${i}} WITH SEED {${seed}}\n\n"
    ./run_intersect_collect.sh v$i $seed;
done
