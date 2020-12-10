import sys
sys.path.append('./src')
import os

def execute(action_arg):
    run_all = action_arg == 'all'
    
    if action_arg == 'clean' or run_all:
        from utils import clean_extra_contents
        clean_extra_contents()
    
    if action_arg == 'env-setup' or run_all:
        os.system('pip install -r requirements.txt --quiet')
        print('Requirements installed!')
        from etl import extract_bd_api
        extract_bd_api()
        print('Building Depot API loaded!')
    
    if action_arg == 'data' or run_all:
        from etl import load_uuid_data, load_co2_and_humidity_data
        load_uuid_data()
        print("Sensor points data loaded in 'sensor_uuids.json'!")
        # Uncomment for checkpoint-3
        # load_co2_and_humidity_data()
        # print("CO2 and Humidity data loaded in the 'data' directory!")
    
    if action_arg == 'test':
        execute('clean')
        execute('data')
        from execute import run_test
        run_test()
        print('Test plot saved in a pdf file inside ./plot/2020-07-30!')
    
    if action_arg == 'plot' or run_all:
        print('Will be fully executed in checkpoint-3. Stay tuned!')
    
    # print('Please specify a valid argument!')

if __name__ == "__main__":
    action = sys.argv[1]
    execute(action)
