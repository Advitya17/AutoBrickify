import pandas as pd
import numpy as np
import os
import sys
sys.path.append('./src')

def automatic_OR(fp='table_743_v1.csv'):
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

    if 'AHU' not in df.UpstreamAHU[random_idx()]:
        df.UpstreamAHU = 'AHU_' + df.UpstreamAHU

    if 'VAV' not in df.VAVName[random_idx()]:
        df.UpstreamAHU = 'VAV_' + df.VAVName

    return df

def execute(action_arg):
    # Alternate way for executing all targets:
    # run_all = action_arg == 'all'
    # or run_all (stripped condition)

    if action_arg == 'clean':
        from utils import clean_extra_contents
        clean_extra_contents()

    elif action_arg == 'env-setup':
        # If need to install requirements:
        # os.system('pip install -r requirements.txt --quiet')
        # print('Requirements installed!')

        # Sets up the BD API in the environment
        # for remote sensors.
        # needed system call to set right permission
        # and load API, as per feedback.
        os.system('chmod +x load_api_and_data.sh')
        os.system('sh load_api_and_data.sh')
        print('Building Depot API loaded!')
        print("CO2 and Humidity data loaded in the 'data' directory!")

    elif action_arg == 'data':
        from etl import load_uuid_data

        load_uuid_data()
        print("Sensor points data loaded in 'config/sensor_uuids.json'!")

        os.system('rm ./data/rm-4140/2930034448-latest.csv')
        print("Data cleaned for automated parsing!")

    elif action_arg == 'test':
        execute('clean')
        execute('env-setup')
        execute('data')
        from execute import run_test
        run_test()
        print('Test plot saved in a pdf file inside ./plot/2020-07-30!')

    elif action_arg == 'all':
        execute('clean')
        execute('env-setup')
        execute('data')
        execute('plot')

    elif action_arg == 'plot':
        from execute import plot
        plot()
        print('All plots saved in ./plot!')

    else:
        print('Please specify a valid argument!')

if __name__ == "__main__":
    automatic_OR(fp='table_743_v1.csv')

    # action = sys.argv[1]
    # need to change
    # execute(action)
