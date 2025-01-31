# Conversion process to COCO format

## Dependency Installation

This repository uses [`poetry`][poetry] to manage dependencies. Ensure your system has poetry installed and then install the environment with `poetry install`. 

## Dataset Management

Once the dataset is created/downloaded, place it in a folder such as `/data/CARLA/my-new-dataset/raw`.

### Generating a new dataset

Follow the main README to generate a new dataset.

### Download an existing dataset

You can download `tar` files for a premade dataset if you have a link. Make sure to untar the files - each run will be a folder. E.g., paths to scenes should be:

```
/data/CARLA/my-new-dataset/raw/run-2025-01-01_01:00:00/s
/data/CARLA/my-new-dataset/raw/run-2025-01-01_01:00:01/
etc.
```
### Dataset inspection

Some jupyter notebooks have been made to inspect the datasets. Those are in this repository in the folder `notebooks`. E.g., look at `test_aerial_dataset.ipynb` or `test_utsa_dataset.ipynb` ensuring that you update paths appropriately. Ensure that you either select the appropriate kernel if running jupyter through VSCode or if from terminal that you activate a poetry shell (e.g., `poetry run jupyter notebook`).


## Coco Conversion

To convert the dataset to the COCO format, we've created some conversion scripts. They are located in the folder `converter`

`run_carla_to_coco.sh` calls the `carla_to_coco.py` conversion script. E.g., a call for our dataset from the `converter` folder would look like,

```
./run_carla_to_coco.sh /data/CARLA/my-new-dataset/raw /data/CARLA/my-new-dataset/coco
```

This will create symbolic links between the `coco` subfolder and the original `raw` subfolder so that we don't duplicate data.

There is an additional input for the stride over the dataset if you want to skip neighboring frames to enhance diversity but at the cost of fewer images.

### Converted inspection

To inspect the converted dataset, we've created some handling classes in `my_coco.py` to aid the `demo_carla_as_coco.ipynb` notebook. Run the notebook with the appropriate dataset paths to verify that things look ok.


[poetry]: https://github.com/python-poetry/poetry
