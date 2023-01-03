# Carla Sandbox -- A Testbed for Autonomous Vehicles

## Philosophy

Testing autonomous vehicles made *easy*.

## Installation

This project is currently organized using submodules. In more stable releases, it will be managed with a package manager like `pip`. For now in an *alpha* stage of development, we stay light on our feet by using submodules and [`poetry`][poetry]

**NOTE:** This currently only works on a Linux distribution (tested on Ubuntu 20.04). It also only works with Python 3.8 (to be expanded in the future).

### Requirements

While Carla does not require use of a GPU, it is highly recommended. Using libraries like `mmdet` (for perception) will certainly require a gpu.

### Preliminaries

#### Repository
First, clone the repository and submodules.
```
git clone --recurse-submodules https://github.com/avstack-lab/carla-sandbox.git
git submodule update --recursive
```

Dependencies are managed with [`poetry`][poetry]. This uses the `pyproject.toml` file to create a `poetry.lock` file. It includes an optional `perception` group so that you can install `avstack` without all the large packages necessary for perception. To install poetry, see [this page](https://python-poetry.org/docs/#installation). 

#### `Docker`
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
```
poetry install
```

#### With Perception

For now, you must set the submodules with perception. This will be fixed in a future release. If you wish to use perception, you must download some of the perception models. To download a pre-selected sample of models, run
```
cd submodules/lib-avstack-core/models
./download_mmdet_models.sh
./download_mmdet3d_models.sh
```

### Download carla egg files

We have pre-compiled some carla eggs to use. You will need to match the Carla version and the Python version to the egg file. You can download the egg file for Carla 0.9.13 and Python 3.8 using
```
cd carla_eggs
./download_carla13_py38_egg.sh
```

## Running

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

Then you can run an example such as
```
cd examples
./run_following_gt_level2.sh 1
```
**Note:** You should be in the `examples` folder before running the example scripts.

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

<details>
<summary>
Cannot create <code>poetry.lock</code> file due to <code>torch</code> dependence of <code>mmdetection</code> build
</summary>
<br>

Still working out how to create a fresh `poetry.lock` file (i.e. when there is not one that exists). If there is one that exists and you do not change `mmdetection` or `mmdetection3d` dependencies, it seems that there is no problem. For now, just don't remove the existing `poetry.lock` file and simply rerun `poetry lock` after a change is made to `pyproject.toml`. 
</details>
<br>


# Contributing

See [CONTRIBUTING.md][contributing] for further details.

# LICENSE

Copyright 2022 Spencer Hallyburton

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

[poetry]: https://github.com/python-poetry/poetry
[docker]: https://www.docker.com/
[nvidia-docker]: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker
[contributing]: https://github.com/avstack-lab/lib-avstack-core/blob/main/CONTRIBUTING.md
[license]: https://github.com/avstack-lab/lib-avstack-core/blob/main/LICENSE.md
