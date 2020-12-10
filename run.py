import sys
sys.path.append('./src')
import os

def execute(action_arg):
    # TODO: remove
    # run_all = action_arg == 'all'
    # or run_all (stripped condition)
    
    if action_arg == 'clean':
        from utils import clean_extra_contents
        clean_extra_contents()
    
    elif action_arg == 'env-setup':
        # TODO: check if need to install requirements
        # remove after documentation update for docker
        # os.system('pip install -r requirements.txt --quiet')
        # print('Requirements installed!')
        
        # needed system call to set right permission 
        # and load API as per feedback
        os.system('chmod +x load_api.sh')
        os.system('sh load_api.sh')
        print('Building Depot API loaded!')
        
        # TODO: remove!
        # from etl import extract_bd_api
        # extract_bd_api()
        # print('Building Depot API loaded!')
    
    elif action_arg == 'data':
        from etl import load_uuid_data, load_co2_and_humidity_data
        
        load_uuid_data()
        print("Sensor points data loaded in 'sensor_uuids.json'!")
        
        load_co2_and_humidity_data()
        print("CO2 and Humidity data loaded in the 'data' directory!")
    
    elif action_arg == 'test':
        # env-setup?
        execute('clean')
        execute('env-setup')
        execute('data')
        # from execute import run_test
        # run_test()
        # print('Test plot saved in a pdf file inside ./plot/2020-07-30!')
        execute('plot')
    
    elif action_arg == 'plot':
        from execute import plot
        plot()
        print('All plots saved in ./plot!')
    
    else:
        print('Please specify a valid argument!')

if __name__ == "__main__":
    action = sys.argv[1]
    execute(action)
