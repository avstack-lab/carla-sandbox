#!/usr/bin/env bash

set -e

for i in {1..10}; do 
    printf "RUN {$i}\n\n"
    ./run_a1_dataset_collection.sh;
done
