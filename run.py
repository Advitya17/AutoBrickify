import sys
sys.path.append('./src')
import os
from etl import load_uuid_data, load_co2_and_humidity_data

if __name__ == "__main__":
    action = sys.argv[1]
    if action == 'env-setup':
        os.system('pip install -r requirements.txt')
        print('Requirements installed!')
    elif action == 'data':
        load_uuid_data()
        print("Sensor points data loaded in 'sensor_uuids.json'!")
        load_co2_and_humidity_data()
        print("CO2 and Humidity data loaded in the 'data' directory")
    else:
        print('Please specify a valid argument!')
