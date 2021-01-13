import pandas as pd
import numpy as np
import os
from abbrmap import abbrmap as tagmap
import json
import brickschema
import re
import sys
sys.path.append('./src')

metadata = {
    "name": "Brick Reconciliation Service",
    "defaultTypes": [
        {"id": "EquipmentClass", "name": "EquipmentClass"},
        {"id": "PointClass", "name": "PointClass"}
    ]
}

inf = brickschema.inference.TagInferenceSession(approximate=True)


def flatten(lol):
    """flatten a list of lists"""
    return [x for sl in lol for x in sl]


def resolve(q):
    """
    q has fields:
    - query: string of the label that needs to be converted to a Brick type
    - type: optional list of 'types' (e.g. "PointClass" above)
    - limit: optional limit on # of returned candidates (default to 10)
    - properties: optional map of property idents to values
    - type_strict: [any, all, should] for strictness on the types returned
    """
    limit = int(q.get('limit', 10))
    # break query up into potential tags
    tags = map(str.lower, re.split(r'[.:\-_ ]', q.get('query', '')))
    tags = list(tags)
    brick_tags = flatten([tagmap.get(tag.lower(), [tag]) for tag in tags])

    if q.get('type') == 'PointClass':
        brick_tags += ['Point']
    elif q.get('type') == 'EquipmentClass':
        brick_tags += ['Equipment']

    res = []
    most_likely, leftover = inf.most_likely_tagsets(brick_tags, limit)
    for ml in most_likely:
        res.append({
            'id': q['query'],
            'name': ml,
            'score': (len(brick_tags) - len(leftover)) / len(brick_tags),
            'match': len(leftover) == 0,
            'type': [{"id": "PointClass", "name": "PointClass"}],
        })
    print('returning', res)
    return res

def automatic_OR(fp='data/table_743_v1.csv'):
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
        from src.utils import clean_extra_contents
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
        from src.etl import load_uuid_data

        load_uuid_data()
        print("Sensor points data loaded in 'config/sensor_uuids.json'!")

        os.system('rm ./data/rm-4140/2930034448-latest.csv')
        print("Data cleaned for automated parsing!")

    elif action_arg == 'test':
        execute('clean')
        execute('env-setup')
        execute('data')
        from src.execute import run_test
        run_test()
        print('Test plot saved in a pdf file inside ./plot/2020-07-30!')

    elif action_arg == 'all':
        execute('clean')
        execute('env-setup')
        execute('data')
        execute('plot')

    elif action_arg == 'plot':
        from src.execute import plot
        plot()
        print('All plots saved in ./plot!')

    else:
        print('Please specify a valid argument!')

if __name__ == "__main__":
    automatic_OR(fp='table_743_v1.csv')

    # action = sys.argv[1]
    # need to change
    # execute(action)
