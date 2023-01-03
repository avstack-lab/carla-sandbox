export CARLA_ROOT=$(realpath "../submodules/carla")
export CARLA_EGGS="../carla_eggs"
export CARLA_VERSION="0.9.13"
export SCENARIO_RUNNER_ROOT="../submodules/scenario_runner"
export LEADERBOARD_ROOT="../submodules/leaderboard"
export PYTHONPATH="${CARLA_EGGS}":"${CARLA_ROOT}/PythonAPI/carla/":${PYTHONPATH}