# Example Runs


## Running Examples

Replace anything in brackets with a "suitable" input. 

- `./run_capture_data_infrastructure.sh`
- `./run_capture_data_random.sh`
- `./run_following_gt_level2.sh <N>`
- `./run_localize_test.sh <N>`

## FAQs

### Why is the client slow to stop running?

The client script pauses for some time (currently set for 10 seconds) to allow any sensor data in memory to be written to disk. This can be controlled in `exec_standard.py`.


### What does "capture_data" mean?

For model training, it can be useful to capture a dataset of simulation data from sensors. This dataset can then be used to train a model or capture statistics on the environment.


### What are infrastructure sensors?

These are sensors placed in places in the environment other than on a vehicle. These could be on traffic lights, buildings, or really anywhere. Being able to use infrastructure sensors for research is vital for the next generation of autonomous vehicle research.


### How do I train a model from the captured data?

Documentation coming soon...