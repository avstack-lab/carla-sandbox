#!/usr/bin/env bash

set -e

cd submodules/OpenCOOD && python opencood/utils/setup.py build_ext --inplace && python setup.py develop
