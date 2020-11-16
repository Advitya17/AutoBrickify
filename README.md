# Zonal Air Handling Replication Project

## Purpose of the offered implementation
Programming a HVAC system to measure and change airflow rates from maximum to minimum and monitor the CO2 Density and Relative Humidity in a classroom and a conference room inside the EBU3B (CSE) building at UC San Diego.

Currently it supports a rudimentary data ingestion component, actions with targets, and has an initial (work in progress in terms of best software engineering practices) implementation of the functions which will be used for the final results for checkpoint-3.

## Contents
The current contents of this rudimentary data ingestion pipeline include:
1. Python file (for ETL processes, convenience utilities, and actual implementations)
2. Documentation (as shown here)
3. Replication paper in `references`
4. The main runnable python script (`run.py`). 
5. 2 params files in the `configs` folder.

## How to run it

1. Set up the environment

`python run.py env-setup`

At the end, you should find `building_depot` API folder in the `/src` folder.

Alternatively, you may build with the `Dockerfile`!

2. Load the sensor data points

`python run.py data`

At the end, you should find `sensor_uuids.json` in the `/configs` folder and a newly fetched `/data` folder

3. Generate the final plots

`python run.py plot` (will be fully functional in checkpoint-3)


### Responsibilities (needed? TODO)

* Devanshu developed the template structure, added the etl file `load_co2_and_humidity_data` function, uploaded the replication paper, and helped in debugging code.
* Advitya developed the README documentation, requirements file, run file, and populated the GitLab json/API files (and related system path support) in the `config` and `src` folder.
