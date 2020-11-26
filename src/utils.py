import os, sys

def clean_extra_contents():
    os.system('rm -rf src/building_depot data plot logs ./config/sensor_uuids.json')
