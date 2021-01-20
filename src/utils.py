import os, sys
import numpy as np

class Schema:
    point_label_col = 'PointLabel'
    ahu_col = 'UpstreamAHU'
    zone_col = 'ZoneName'
    vav_col = 'VAVName'
    brick_class_col = 'BrickClass'
    temp_col = '_'
    col_list = [point_label_col, ahu_col, zone_col, vav_col, brick_class_col]
    ahu_prefix = 'AHU_'
    vav_prefix = 'VAV_'

def random_idx(n):
    return np.random.randint(0, n)

def recon_api_inference():
    """
    TODO!!
    """
    pass

def clean_extra_contents():
    os.system('rm -rf src/building_depot data plot logs ./config/sensor_uuids.json')


