# re-factored from https://gitlab.com/dzhong1989/hvac-safety-control/-/blob/master/experiment.py

import pprint
import pdb
import arrow
import json
import sys
import os
import time
import logging
import csv

from datetime import timedelta
from cycler import cycler

from glob import glob

RETRYLIMIT = 2

# # create logging directory if not exists yet
# try:
#     os.mkdir('logs', 0o755)
# except FileExistsError:
#     pass
# # setup loggings
# logging.basicConfig(filename=f'logs/{arrow.now().format()}.log',level=logging.DEBUG)

def random_idx(n):
    return np.random.randint(0, n)

def automatic_OR():
    # load config
    config = json.load(open('config/data-params.json'))
    fp = config["fp"]
    drop_null_rows = config["drop_null_rows"]
    
    remote_sensors = config["remote_sensors"]
    
    """Automates work of Open Refine"""
    df = pd.read_csv(fp)

    def random_idx():
        return np.random.randint(0, len(df))

    # naming conventions followed in column names

    df = df[['description', 'jci_name']]
    df.rename({'jci_name': 'PointLabel'}, axis=1)

    # hard-coded
    df[['_', 'UpstreamAHU', 'ZoneName', 'VAVName', 'BrickClass', '_']] = df.jci_name.str.split('.', expand=True)
    df = df.drop('_', axis=1)
    if drop_null_rows:
        df = df.dropna()
    
    n = len(df)

    if 'AHU' not in df.UpstreamAHU[random_idx(n)]:
        df.UpstreamAHU = 'AHU_' + df.UpstreamAHU

    if 'VAV' not in df.VAVName[random_idx(n)]:
        df.UpstreamAHU = 'VAV_' + df.VAVName

    return df


