# Zonal Air Handling Replication Project

## Purpose of the offered implementation
Programming a HVAC system to measure and change airflow rates from maximum to minimum and monitor the CO2 Density and Relative Humidity in a classroom and a conference room inside the EBU3B (CSE) building at UC San Diego.

Currently it supports a rudimentary data ingestion component, actions with targets, and has an initial (work in progress in terms of best software engineering practices) implementation of the functions which is used with some testing data.

## Contents
The current contents of this repository include:
1. Python files (for ETL processes, convenience utilities, and actual implementations)
2. Documentation (as shown here)
3. Replication paper in `references`
4. The main runnable python script (`run.py`). 
5. Params files in the `configs` folder.

## How to run it

### For Methdology 7

1. Set up the environment by building with the `Dockerfile`. Alternatively, you may use:

`python run.py env-setup`

2. Run `python run.py test` to get results with some test data.

### General Instructions

1. Set up the environment

`python run.py env-setup`

At the end, you should find `building_depot` API folder in the `/src` folder.

Alternatively, you may build with the `Dockerfile`!

2. Load the sensor data points

`python run.py data`

At the end, you should find `sensor_uuids.json` in the `/configs` folder and a newly fetched `/data` folder

3. Generate the final plots

`python run.py plot` (will be fully functional in checkpoint-3)

