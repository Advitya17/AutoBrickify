# Zonal Air Handling Replication Project

## Purpose of the offered implementation
Programming a HVAC system to measure and change airflow rates from maximum to minimum and monitor the CO2 Density and Relative Humidity in a classroom and a conference room inside the EBU3B (CSE) building at UC San Diego.

Currently it only supports a rudimentary data ingestion component, as per the purposes of Checkpoint-1.

## Contents
The current contents of this rudimentary data ingestion pipeline include:
1. ETL function (`./src/etl.py`)
2. Documentation (as shown here)
3. The main runnable python script (`run.py`)
4. Params file (`./config/data-params.json`)

## How to run it

1. Set up the environment

`python run.py env-setup`

2. Load the sensor data points

`python run.py data`
