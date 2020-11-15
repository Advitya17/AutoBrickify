# Everything except the 'load_co2_and_humidity_data' function is taken from:
# https://gitlab.com/dzhong1989/hvac-safety-control/-/blob/master/experiment.py

import pprint
import pdb
import arrow
import json
import sys
import os
import time
import logging
import csv

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator, AutoMinorLocator, AutoLocator, FixedLocator
from building_depot import DataService, BDError
from datetime import timedelta
from cycler import cycler

# sys.path.append('../config')

# load config
config = json.load(open('config/data-params.json')) # '../data-params.json'
cse_dataservice_url = config["cse_dataservice_url"]
bd_username = config["bd_username"]
bd_api_key = config["bd_api_key"]
remote_sensors = config["remote_sensors"]

etl_config = json.load(open('config/etl-params.json')) # '../data-params.json'
source_repo = etl_config["source_repo"]
repo_name = etl_config["repo_name"]
api_fp = etl_config["api_fp"]
data_fp = etl_config["data_fp"]

#Connect with BuildingDepot
ds = DataService(cse_dataservice_url, bd_api_key, bd_username)

def extract_bd_api():
    os.system('git clone ' + source_repo)
    os.system('mv ' + api_fp + ' ../src/building_depot')
    os.system('rm -rf ./' + repo_name)

def load_uuid_data():
    data = {}
    for room in list(config["target_rooms_setpoint_values"].keys())+list(config["uncontrolled_rooms"].keys()):
        query = {
            'room': room
        }
        resp = ds.list_sensors(query)
        uuids = {sensor['template']: sensor['uuid'] for sensor in resp['sensors'] if sensor['template'] in remote_sensors}
        data[room] = uuids

    with open('config/sensor_uuids.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

def load_co2_and_humidity_data():
    os.system('git clone ' + source_repo)
    os.system('mv ' + data_fp + ' ../src/data')
    # os.system('mv ../CO2_data ../data')
    os.system('rm -rf ./' + repo_name)

