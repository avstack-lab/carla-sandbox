# Carla Sandbox -- A Testbed for Autonomous Vehicles

## Installation

This project is currently organized using submodules. In more stable releases, it will be managed with a package manager like `pip`. For now in an *alpha* stage of development, we stay light on our feet by using submodules and [`poetry`][poetry]

**NOTE:** This currently only works on a Linux distribution (tested on Ubuntu 20.04 and 22.04). It also only works with Python 3.10 (to be expanded in the future).

### Requirements

While Carla does not require use of a GPU, it is highly recommended. Using libraries like `mmdet` (for perception, as in [`avstack-core`][avstack-core]) will require a gpu.

### Preliminaries

#### Repository
First, clone the repository and submodules.
```
git clone --recurse-submodules https://github.com/avstack-lab/carla-sandbox.git
git submodule update --recursive
```

Dependencies are managed with [`poetry`][poetry]. This uses the `pyproject.toml` file to create a `poetry.lock` file. To install poetry, see [this page](https://python-poetry.org/docs/#installation). 

#### `Docker` - last updated June 2023
If [`docker`][docker] is not installed, install with something like
```
curl https://get.docker.com | sh \
  && sudo systemctl --now enable docker
```

Verify `docker` with `docker run hello-world`.

#### NVIDIA Container Toolkit
If [`nvidia-docker2`][nvidia-docker] is not installed, run something like
```
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
      && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
      && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

Verify `nvidia-docker2` is working with 
```
sudo docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
```

### Install Dependencies

#### Environment
Will take about 2-3 minutes, depending on your cpu count.
```
poetry install
```

#### (optional) Models/Datasets
Will take about 5 minutes the first time you download.
```
./initialize.sh
```

## Running a basic example

### First: run carla through any shell (uses docker)
For example, run
```
cd run_carla
./run_carla_0913.sh
```

### Then: run an example through a poetry shell
The examples are run as shell scripts. Therefore, you have to first activate the environment with
```
poetry shell
```

Try running a non-perception example such as:
```
cd examples
./run_a0_autopilot.sh
```

**Note:** You should be in the `examples` folder before running the example scripts.


## Collecting a Multi-Agent Dataset
With the `carla` server already running, run the dataset collection script:
```
poetry shell
cd examples
./run_a1_dataset_collection.sh
```

This will log data to the folder `sim_results/`. To use the dataset, we need to run postprocessing. With the poetry shell activated, navigate to `submodules/lib-avstack-carla`. Run the postprocessing:
```
python postprocess_carla_objects.py ../../examples/sim_results
```
This will take some time, depending on how long you ran the simulation. After postprocessing is complete, inspect the dataset by going back to the `notebooks/` folder and opening `test_carla_dataset.ipynb`.

## Troubleshooting
<!-- NOTE: remember to put a line break for any markdown commands in HTML. Otherwise, you need to use only HTML commands-->

<!-- <details>
<summary>
TODO
</summary>
<br>
TODO
</details> -->

<details>
<summary>
Docker claims permission denied
</summary>
<br>

Your user must be able to run docker commands. On some configurations, this may amount to adding the user to the `docker` user group. Contact your system admin.
</details>
<br>

<details>
<summary>
CARLA docker is not displaying
</summary>
<br>

If the docker container process was previously running for a *different* user, it may be trying to show the display for that other user. Check if there is a process using `docker ps -a` to get the ID's of any containers running and use `docker rm <CONTAINER ID HERE>` to officially stop and remove a process before trying again.
</details>
<br>
<br>


# Contributing

See [CONTRIBUTING.md][contributing] for further details.

# LICENSE

Copyright 2023 Spencer Hallyburton

AVstack specific code is distributed under the MIT License.

[poetry]: https://github.com/python-poetry/poetry
[docker]: https://www.docker.com/
[nvidia-docker]: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker
[avstack-core]: https://github.com/avstack-lab/lib-avstack-core
[avstack-api]: https://github.com/avstack-lab/lib-avstack-api
[contributing]: https://github.com/avstack-lab/lib-avstack-core/blob/main/CONTRIBUTING.md
[license]: https://github.com/avstack-lab/lib-avstack-core/blob/main/LICENSE.md
