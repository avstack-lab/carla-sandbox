#!/bin/bash

find_in_conda_env(){
    conda env list | grep "${@}" >/dev/null 2>/dev/null
}

# Install conda itself
MCFILE="Miniconda3-py38_4.12.0-Linux-x86_64.sh"
if ! command -v conda &> /dev/null
then
    echo "conda is not installed!"
    while true; do
        read -p "Do you wish to install miniconda? (y/n)? " yn
        case $yn in
          [Yy]* ) wget "https://repo.anaconda.com/miniconda/$MCFILE" && \
                  chmod +x "$MCFILE" && \
                  bash "MCFILE"; break;;
          [Nn]* ) exit;;
          * ) echo "Please answer yes or no.";;
      esac
    done  
fi

# set up conda environment
CENV="carla-sandbox"
#CENV="carla-sandbox-mmlab"
if find_in_conda_env "$CENV"; then
    echo "Found existing conda environment"
else
    echo "Creating conda environment"
    conda env create -f "../environments/$CENV.yml"
fi
conda activate $CENV

# set up submodules
bash "install_modules.sh"

# set up docker
if ! command -v docker &> /dev/null
then
    echo "docker is not installed...?"
    while true; do
      read -p "Do you wish to install this docker (y/n)? " yn
      case $yn in
          [Yy]* ) bash "install_docker.sh"; break;;
          [Nn]* ) exit;;
          * ) echo "Please answer yes or no.";;
      esac
    done  
fi

# set up nvidia-docker
if ! command -v nvidia-docker &> /dev/null
then
    echo "nvidia-docker is not installed...?"
    while true; do
      read -p "Do you wish to install this docker (y/n)? " yn
      case $yn in
          [Yy]* ) bash "install_nvidia-docker.sh"; break;;
          [Nn]* ) exit;;
          * ) echo "Please answer yes or no.";;
      esac
    done  
fi

# set up carla
bash "../run_carla_0913.sh"
echo "Delaying for 10 to allow for loading"
sleep 10

# run an example
cd ../examples && bash run_overtake_gt.sh 1

echo "done"
