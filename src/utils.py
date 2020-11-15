import os, sys

def clean_extra_contents():
    os.system('rm -rf ./building_depot ../data ../plots /config/sensor_uuids.json')
