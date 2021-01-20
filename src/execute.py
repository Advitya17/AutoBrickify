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

class Schema:
    point_label_col = 'PointLabel'
    ahu_col = 'UpstreamAHU'
    zone_col = 'ZoneName'
    vav_col = 'VAVName'
    brick_class_col = 'BrickClass'
    temp_col = '_'
    col_list = [point_label_col, ahu_col, zone_col, vav_col, brick_class_col]

def random_idx(n):
    return np.random.randint(0, n)

def validate_plf(point_label_col):
    # TODO: some assumptions may need to be validated
    
    assert all(cn in repr(point_label_col) for c in col_list), 'all column names are not utilized!'
    assert len(point_label_col) == len(set(point_label_col)), 'specified column names are not unique!'

def get_split_col_names(point_label_format):
    # ['_', 'UpstreamAHU', 'ZoneName', 'VAVName', 'BrickClass', '_']
    split_cols = []
    replications = {}
    
    for pl in point_label_format:
        if pl is None:
            res.append(Schema.temp_col)
        elif type(pl) == str:
            res.append(pl)
        elif type(pl) == list:
            res.append(pl[0])
            replications[pl[0]] = pl[1:]
        else:
            raise TypeError # invalid point label format type
    
    return split_cols, replications

def get_ordered_cols(split_cols, replications):
    ordered_cols = []
    for sc in split_cols:
        if sc not in replications:
            ordered_cols.append(sc)
        else:
            for c in replications[sc]:
                df[c] = df[sc]
                ordered_cols.append(c)
     return ordered_cols

def automatic_OR():
    """Automates work of Open Refine"""
    
    # load config
    config = json.load(open('config/data-params.json'))
    fp = config['fp']
    point_label_col = config['point_label_col']
    delimiter = config['delimiter']
    point_label_format = config['point_label_format']
    drop_null_rows = config['drop_null_rows']
    
    validate_plf(point_label_col)
    
    df = pd.read_csv(fp)

    # naming conventions followed in column names

    df = df[[point_label_col]]
    df.rename({point_label_col: Schema.point_label_col}, axis=1)

    split_cols, replications = get_split_col_names(point_label_format)
    df[split_cols] = df.jci_name.str.split(delimiter, expand=True)
    df = df.drop(Schema.temp_col, axis=1)
    
    ordered_cols = get_ordered_cols(split_cols, replications)
    df = df[ordered_cols]
    
    df = df.dropna() if drop_null_rows
    
    n = len(df)

    if 'AHU' not in df.UpstreamAHU[random_idx(n)]:
        df.UpstreamAHU = 'AHU_' + df.UpstreamAHU

    if 'VAV' not in df.VAVName[random_idx(n)]:
        df.UpstreamAHU = 'VAV_' + df.VAVName

    return df


