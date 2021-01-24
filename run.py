import pandas as pd
import numpy as np
import os
from abbrmap import abbrmap as tagmap
import json
import brickschema
import re
import sys
sys.path.append('./src')

def run(action_arg):
    """Utilized later"""

    if action_arg == 'clean':
        from src.utils import clean_extra_contents
        clean_extra_contents()

    elif action_arg == 'env-setup':
        # If need to install requirements:
        os.system('pip install -r requirements.txt --quiet')
        print('Requirements installed!')
        
        os.system('chmod +x load_api_and_data.sh')
        os.system('sh load_api_and_data.sh')

    elif action_arg == 'all':
        execute('clean')
        execute('env-setup')
        execute('brickify')

    elif action_arg == 'brickify':
        from src.execute import automatic_OR
        
        filename = automatic_OR(filename='output.ttl')
    
        # TODO: transfer to load_data_and_api.sh file
        os.system('python brick-builder/make.py brick_builder_example.txt:' + filename)

    else:
        print('Please specify a valid argument!')

if __name__ == "__main__":
    action = sys.argv[1]
    execute(action)
