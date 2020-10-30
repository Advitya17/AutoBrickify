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
# from building_depot import DataService, BDError
from datetime import timedelta
from cycler import cycler
from etl import load_uuid_data, load_co2_data

sys.path.append('./src')

if __name__ == "__main__":
    action = sys.argv[1]
    if action == 'env-setup':
        os.system('pip install -r requirements.txt')
        print('Requirements installed!')
    elif action == 'data':
        load_uuid_data()
        print("Sensor points data loaded in 'sensor_uuids.json'!")
        load_co2_data()
        print("CO2 and Humidity data loaded in the 'data' directory")
    else:
        print('Please specify a valid argument!')
