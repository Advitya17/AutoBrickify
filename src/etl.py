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

sys.path.append('../config')

# load config
config = json.load(open('data-params.json')) # '../data-params.json'
cse_dataservice_url = config["cse_dataservice_url"]
bd_username = config["bd_username"]
bd_api_key = config["bd_api_key"]
# session_length = config["session_length"] # not used so far
remote_sensors = config["remote_sensors"]
# local_sensors = config["local_sensors"] # not used so far
actuation_target_sensor = config["actuation_target_sensor"]

#Connect with BuildingDepot
ds = DataService(cse_dataservice_url, bd_api_key, bd_username)

def load_uuid_data():
    data = {}
    for room in list(config["target_rooms_setpoint_values"].keys())+list(config["uncontrolled_rooms"].keys()):
        query = {
            'room': room
        }
        resp = ds.list_sensors(query)
        uuids = {sensor['template']: sensor['uuid'] for sensor in resp['sensors'] if sensor['template'] in remote_sensors}
        data[room] = uuids

    with open('../sensor_uuids.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)
