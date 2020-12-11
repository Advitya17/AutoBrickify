# Zonal Air Handling Replication Project

## Purpose of the offered implementation
Programming a HVAC system to measure and change airflow rates from maximum to minimum and monitor the CO2 Density and Relative Humidity in a classroom and a conference room inside the EBU3B (CSE) building at UC San Diego.

Currently it supports a data ingestion component, actions with targets, and has the final implementation of the functions used with a testing sample and all extracted datasets.

## Contents
The current contents of this repository include:
1. Python files (for ETL processes, convenience utilities, and actual implementations)
2. Documentation (as shown here)
3. Replication paper in `references`
4. The main runnable python script (`run.py`). 
5. Params files in the `configs` folder.

## Instructions to runt he project

1. Set up the environment by building with the `Dockerfile`. Alternatively, you may use:

`pip install -r requirements.txt`

2. Go into the project root (github repo directory):

`cd 180A_result_replication`

3. For getting results with the testing data sample, run

`python run.py test`

4. For getting results with the all extracted datasets, run

`python run.py all`

It'll take ~6 minutes to run the `all` target.

### Feedback Responses

* why can't you take the figures that you save and use them in a notebook/report?

Done in the final report!

* Avoid os.system if you can (prefer python's rename).

The added shell file helped in directory renaming and reducing os.system calls. 

* Usually, git clone shouldn't be called in library code (should be part of environment setup -- probably easier to put in a bash script).

We have included it in our `env-setup` target and invoke a shell file to load the API.
