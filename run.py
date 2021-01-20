import pandas as pd
import numpy as np
import os
from abbrmap import abbrmap as tagmap
import json
import brickschema
import re
import sys
sys.path.append('./src')

from src.execute import automatic_OR

def run(action_arg):
    """Utilized later"""

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
        pass

    elif action_arg == 'data':
        pass

    elif action_arg == 'test':
        pass

    elif action_arg == 'all':
        execute('clean')
        execute('env-setup')
        execute('data')
        execute('plot')

    elif action_arg == 'plot':
        pass

    else:
        print('Please specify a valid argument!')

if __name__ == "__main__":
    filename = automatic_OR(filename='output.ttl')
    
    os.system('git clone https://github.com/gtfierro/brick-builder')
    os.system('python make.py brick_builder_example.txt:' + filename)

    # action = sys.argv[1]
    # need to change
    # execute(action)
