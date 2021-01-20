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
from utils import *

# RETRYLIMIT = 2
# 
# # create logging directory if not exists yet
# try:
#     os.mkdir('logs', 0o755)
# except FileExistsError:
#     pass
# # setup loggings
# logging.basicConfig(filename=f'logs/{arrow.now().format()}.log',level=logging.DEBUG)

def validate_plf(point_label_col):
    # TODO: some assumptions may need to be validated
    
    # assert all(cn in repr(point_label_col) for c in col_list), 'all column names are not utilized!'
    # assert len(point_label_col) == len(Schema.col_list), 'specified column names are not unique!'
    
    num_cols = 0
    flattened_plcs = []
    for i in point_label_col:
        if pl is None:
            continue
        elif type(pl) == str:
            assert pl in Schema.col_list, '{0} is an invalid col name'.format(pl)
            num_cols += 1
            flattened_plcs.append(pl)
        elif type(pl) == list:
            for p in pl:
                assert type(pl) == str, 'invalid type for nested col name {0}'.format(pl)
                assert pl in Schema.col_list, '{0} is an invalid col name'.format(pl)
                num_cols += 1
                flattened_plcs.append(pl)
        else:
            raise TypeError # invalid point label format type
    
    assert num_cols == len(Schema.col_list), 'all column names are not utilized!'
    assert len(set(flattened_plcs)) == num_cols, 'number of column names do not match!'
            

def get_split_col_names(point_label_format):
    # for example - ['_', 'UpstreamAHU', 'ZoneName', 'VAVName', 'BrickClass', '_']
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
    """See if needed"""
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
    pat = config['delimiter']['pattern']
    regex = config['delimiter']['regex']
    pat = pat.encode('unicode-escape').decode() if regex # converts to regex string as per user preference
    point_label_format = config['point_label_format']
    drop_null_rows = config['drop_null_rows']
    
    # INFO: naming conventions followed in column names
    validate_plf(point_label_col)
    
    df = pd.read_csv(fp)
    
    # STEP 1: AUTOMATING ALL DATA TRANSFORMATIONS
    df = df[[point_label_col]]
    df = df.rename({point_label_col: Schema.point_label_col}, axis=1)

    split_cols, replications = get_split_col_names(point_label_format)
    # try:
    df[split_cols] = df[Schema.point_label_col].str.split(pat, expand=True)
    # except: # TODO: find out error type
    #     print('Number of columns not matching number of words separated from the \
    #     point labels with the specified delimiter')
    df = df.drop(Schema.temp_col, axis=1)
    
    # ordered for Brick Builder
    df = df[Schema.col_list] # get_ordered_cols(split_cols, replications)
    
    df = df.dropna() if drop_null_rows
    
    n = len(df)
    
    # needed ??
    df[Schema.ahu_col] = Schema.ahu_prefix + df[Schema.ahu_col].str.replace(Schema.ahu_prefix[:-1].lower(), 
                                                                            '').replace(Schema.ahu_prefix[:-1], '')
    df[Schema.vav_col] = Schema.vav_prefix + df[Schema.vav_col].str.replace(Schema.vav_prefix[:-1].lower(), 
                                                                            '').replace(Schema.ahu_prefix[:-1], '')
    
    # STEP 2: RECONCILIATION API INJECTION
    df[Schema.brick_class_col] = df[Schema.brick_class_col].apply(recon_api_inference)
    
    # (STEP 3: BRICK BUILDER: COMING SOON)

    return df


