# re-factored from https://gitlab.com/dzhong1989/hvac-safety-control/-/blob/master/experiment.py

import pprint
import pdb
import arrow
import json
import sys
import os
import time
import logging
import csv

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator, AutoMinorLocator, AutoLocator, FixedLocator
# from building_depot import DataService, BDError
from datetime import timedelta
from cycler import cycler


plt.rcParams["font.family"] = "serif"
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['axes.labelsize'] = 20
plt.rcParams['figure.titlesize'] = 20
plt.rcParams['legend.fontsize'] = 20
plt.rcParams['font.size'] = 18

RETRYLIMIT = 2

# create logging directory if not exists yet
try:
    os.mkdir('logs', 0o755)
except FileExistsError:
    pass
# setup loggings
logging.basicConfig(filename=f'logs/{arrow.now().format()}.log',level=logging.DEBUG)

# load config
config = json.load(open('../config/data-params.json'))
cse_dataservice_url = config["cse_dataservice_url"]
bd_username = config["bd_username"]
bd_api_key = config["bd_api_key"]
remote_sensors = config["remote_sensors"]
local_sensors = config["local_sensors"] # not used so far
actuation_target_sensor = config["actuation_target_sensor"]

#Connect with BuildingDepot
ds = DataService(cse_dataservice_url, bd_api_key, bd_username)

def get_remote_sensor_plot_details(axarr, lgds):
    ax1 = axarr[0] if has_locals else axarr # axes for air flow
    ax3 = ax1.twinx() # axes for temperature

    lines1 = {} # lines on ax1 and ax3 (CFM, temp)

    ##############################
    # read remote sensors & plot #
    ##############################
    for sensor in remote_sensors:
        # skip
        if sensor == 'Actual Sup Flow SP':
            continue
        if sensor == 'Reheat Valve Command':
            continue
        # get uuid
        try:
            sensor_uuid = uuids[room][sensor]
        except KeyError:
            print(f'{room} does not have sensor point for {sensor}, skipped.')
            logging.warning(f'{room} does not have sensor point for {sensor}, skipped.')
            continue
        # get data from remote and preproceed
        data = ds.get_timeseries_datapoints(sensor_uuid, 'PresentValue', str(start_time), str(end_time))
        data = {k:v for d in data['timeseries'] for k, v in d.items()}
        time = [arrow.get(t).datetime for t in list(data.keys())]
        value = list(data.values())

        # plot
        if sensor == 'Actual Supply Flow':
            # comma here is to unpack line from list
            line, = ax1.plot(time, value, linewidth=3, label='Supply Air Flow', color='tab:blue')

            # plot equivalent ACH mark line at max airflow
            rate = config["ACH_Rate"][room]
            marks = [rate * 5] * len(time) # marks = [max(set(value), key=value.count)]*len(time)
            markline, = ax1.plot(time, marks, ':', linewidth=3, label="Equivalent ACH", color='black')
            text_pos = (-27, 6) if room not in ["rm-2219"] else (-27,-20)
            ax1.annotate(f'{marks[0]/rate:2.1f}ACH', xy=(time[0], marks[0]), xycoords='data', xytext=text_pos, textcoords='offset pixels', ha='left')
            lines1[sensor] = line
            lines1["ACH Mark"] = markline

        elif sensor == 'Zone Temperature':
            line, = ax3.plot(time, value, linewidth=3, label='Zone Air Temperature', color='tab:orange')
            lines1[sensor] = line

        elif sensor == 'Actual Heating Setpoint':
            line, = ax3.plot(time, value, linestyle=(0, (5, 5)), linewidth=1.5, label='Temperature Lower Bound', color='tab:grey')
            lines1[sensor] = line

        elif sensor == 'Actual Cooling Setpoint':
            line, = ax3.plot(time, value, '-.', linewidth=1.5, label='Temperature Upper Bound', color='tab:grey')
            lines1[sensor] = line

    if room in config["uncontrolled_rooms"]:
        controlled_room = config["uncontrolled_rooms"][room]
        title = f'Summary of {room} (vs. {controlled_room}) on {start_time.format("YYYY-MM-DD")}'
        filename = f'{path}/{room}(vs. {controlled_room}).pdf'
    else:
        title = f'Summary of {room} on {start_time.format("YYYY-MM-DD")}'
        filename = f'{path}/{room}.pdf'

    #########################
    # configure ax1 and ax3 #
    #########################
    lcolor = lines1['Actual Supply Flow'].get_color()
    ax1.set_ylabel('Airflow (CFM)', color=lcolor)
    ax1.tick_params(axis='y', labelcolor=lcolor, color=lcolor)

    if room == 'rm-4140':
        ax1.set_ylim(-20.0, 2673.4265)
        controlled_axes_range[room] = {'ax1':ax1.get_ylim()}
    elif room not in config["uncontrolled_rooms"]:
        ax1.set_ylim(ymin=-20)
        controlled_axes_range[room] = {'ax1':ax1.get_ylim()}
    else:
        ax1.set_ylim(controlled_axes_range[controlled_room]['ax1'])

    lcolor = lines1['Zone Temperature'].get_color()
    ax3.set_ylim(64, 81)
    ax3.tick_params(axis='y', labelcolor=lcolor, color=lcolor)
    ax3.set_ylabel('Temperature (F)', color=lcolor)
    ax3.yaxis.set_major_locator(MultipleLocator(5))

    ax1.xaxis.set_major_locator(hours)
    ax1.xaxis.set_major_formatter(hours_formatter)
    ax1.grid(True)

    lgd = ax1.legend(list(lines1.values()), [l.get_label() for l in lines1.values()], loc='center', bbox_to_anchor=(0.5, 1.19),
        fancybox=True, shadow=True, ncol=2)
    lgds.append(lgd)
    ax1.set_title(title,y=1.37)

def get_local_sensor_plot_details(axarr, lgds):
    ax2 = axarr[1] # axes for CO2
    ax4 = ax2.twinx() # axes for humidity
    
    lines2 = {} # lines on ax2 and ax4 (co2, humidity)
    
    ##################################       
    # read local sensors data & plot #
    ##################################
    with open(f'CO2_data/{room}/{str(start_time.date())}.csv') as csvFile:
        reader = csv.reader(csvFile, delimiter=',', quotechar='"')
        next(reader)
        time, co2, humidity = [], [], []
        for row in reader:
            t = arrow.get(row[0])
            if t < start_time:
                continue
            time.append(t.datetime)
            co2.append(float(row[1]))
            humidity.append(float(row[2]))
        # co2
        line_co2, = ax2.plot(time, co2, linewidth=3, label='CO2 Density', color='tab:red')
        lines2["Carbon Dioxide Concentration"] = line_co2

        # humidity
        line_humidity, = ax4.plot(time, humidity, linewidth=3, label='Relative Humidity', color='tab:purple')
        lines2["Humidity"] = line_humidity
    
    lgd = ax1.legend(list(lines1.values()), [l.get_label() for l in lines1.values()], loc='lower center', bbox_to_anchor=(0.5, 0.98),
                    fancybox=True, shadow=True, ncol=2)
    lgds.append(lgd)
    ax1.set_title(title, y=1.43)
    
    #########################
    # configure ax2 and ax4 #
    #########################
    ax2.set_ylim(350,450)
    lcolor = lines2['Carbon Dioxide Concentration'].get_color()
    ax2.set_ylabel('CO2 Density (ppm)', color=lcolor)
    ax2.tick_params(axis='y', labelcolor=lcolor, color=lcolor, which='both')
    ax2.yaxis.set_minor_locator(AutoMinorLocator())

    # print(ax4.get_ylim())
    ax4.set_ylim(58.525, 71.575)
    lcolor = lines2['Humidity'].get_color()
    ax4.set_ylabel('Humidity (%)', color=lcolor)
    ax4.tick_params(axis='y', labelcolor=lcolor, color=lcolor)
    ax4.yaxis.set_major_locator(MultipleLocator(0.5))
    ax4.yaxis.set_major_locator(MultipleLocator(2))

    ax2.grid(True)

    lgd = ax2.legend(list(lines2.values()), [l.get_label() for l in lines2.values()], loc='lower center', bbox_to_anchor=(0.5, 0.98),
        fancybox=True, shadow=True, ncol=2)
    lgds.append(lgd)

# create plots for certain period
def plot():
    for start_time in glob('../'):
        start_time = arrow.get(start_time).shift(hours=7)
        uuids = json.load(open('sensor_uuids.json'))
        PT = 'US/Pacific'
        start_time = start_time.to(PT)
        # start_time = arrow.get(2020, 8, 2, 0, 0, 0, tzinfo=PT) # change this parameter for different sessions
        end_time = start_time.shift(days=1)
        start_time = start_time.shift(hours=7)
        tzPT = start_time.tzinfo

        # create plot directory for this experiment
        try:
            os.mkdir('../plot', 0o755)
        except FileExistsError:
            pass
        path = f'../plot/{start_time.format("YYYY-MM-DD")}'
        try:
            os.mkdir(path, 0o755)
        except FileExistsError:
            pass

        hours = mdates.HourLocator(byhour=range(0,24,2))
        # tenmin = mdates.MinuteLocator(byminute=range(0, 60, 10))
        hours_formatter = mdates.DateFormatter('%b-%d %H:%M', tz=tzPT)
        # tenmin_formatter = mdates.DateFormatter('%H:%M', tz=tzPT)

        controlled_axes_range = {}

        for room in list(config["target_rooms_setpoint_values"].keys())+list(config["uncontrolled_rooms"].keys()):
            has_locals = room in config["room_with_locals"]
            print(room, has_locals) # remove
            
            # two subplots, upper one contains ax1/3, lower one contains ax2/4
            fig, axarr = plt.subplots(2, sharex=True, figsize=(10.5,11)) if has_locals else plt.subplots(1, figsize=(10.5,6))
            lgds = []
            get_remote_sensor_plot_details(axarr, lgds)
            
            if has_locals:
                get_local_sensor_plot_details(axarr, lgds) # POSITIONING if needed

            ########################
            # configure fig & save #
            ########################
            fig.autofmt_xdate()
            plt.savefig(filename, bbox_extra_artists=lgds, bbox_inches='tight')
            plt.close()

def run_test():
    # todo
    start_time = 'HARDCODE' # TODO
    uuids = json.load(open('sensor_uuids.json'))
    PT = 'US/Pacific'
    start_time = start_time.to(PT)
    # start_time = arrow.get(2020, 8, 2, 0, 0, 0, tzinfo=PT) # change this parameter for different sessions
    end_time = start_time.shift(days=1)
    start_time = start_time.shift(hours=7)
    tzPT = start_time.tzinfo

    # create plot directory for this experiment
    try:
        os.mkdir('../plot', 0o755)
    except FileExistsError:
        pass
    path = f'../plot/{start_time.format("YYYY-MM-DD")}'
    try:
        os.mkdir(path, 0o755)
    except FileExistsError:
        pass

    hours = mdates.HourLocator(byhour=range(0,24,2))
    # tenmin = mdates.MinuteLocator(byminute=range(0, 60, 10))
    hours_formatter = mdates.DateFormatter('%b-%d %H:%M', tz=tzPT)
    # tenmin_formatter = mdates.DateFormatter('%H:%M', tz=tzPT)

    controlled_axes_range = {}
    
    room = 'HARDCODE'

    has_locals = room in config["room_with_locals"]
    print(room, has_locals) # remove

    # two subplots, upper one contains ax1/3, lower one contains ax2/4
    fig, axarr = plt.subplots(2, sharex=True, figsize=(10.5,11)) if has_locals else plt.subplots(1, figsize=(10.5,6))
    lgds = []
    # get_remote_sensor_plot_details(axarr, lgds)
    ax1 = axarr[0] if has_locals else axarr # axes for air flow
    ax3 = ax1.twinx() # axes for temperature

    lines1 = {} # lines on ax1 and ax3 (CFM, temp)

    ##############################
    # read remote sensors & plot #
    ##############################
    for sensor in remote_sensors:
        # skip
        if sensor == 'Actual Sup Flow SP':
            continue
        if sensor == 'Reheat Valve Command':
            continue
        # get uuid
        try:
            sensor_uuid = uuids[room][sensor]
        except KeyError:
            print(f'{room} does not have sensor point for {sensor}, skipped.')
            logging.warning(f'{room} does not have sensor point for {sensor}, skipped.')
            continue
        # get data from remote and preproceed
        data = ds.get_timeseries_datapoints(sensor_uuid, 'PresentValue', str(start_time), str(end_time))
        data = {k:v for d in data['timeseries'] for k, v in d.items()}
        time = [arrow.get(t).datetime for t in list(data.keys())]
        value = list(data.values())

        # plot
        if sensor == 'Actual Supply Flow':
            # comma here is to unpack line from list
            line, = ax1.plot(time, value, linewidth=3, label='Supply Air Flow', color='tab:blue')

            # plot equivalent ACH mark line at max airflow
            rate = config["ACH_Rate"][room]
            marks = [rate * 5] * len(time) # marks = [max(set(value), key=value.count)]*len(time)
            markline, = ax1.plot(time, marks, ':', linewidth=3, label="Equivalent ACH", color='black')
            text_pos = (-27, 6) if room not in ["rm-2219"] else (-27,-20)
            ax1.annotate(f'{marks[0]/rate:2.1f}ACH', xy=(time[0], marks[0]), xycoords='data', xytext=text_pos, textcoords='offset pixels', ha='left')
            lines1[sensor] = line
            lines1["ACH Mark"] = markline

        elif sensor == 'Zone Temperature':
            line, = ax3.plot(time, value, linewidth=3, label='Zone Air Temperature', color='tab:orange')
            lines1[sensor] = line

        elif sensor == 'Actual Heating Setpoint':
            line, = ax3.plot(time, value, linestyle=(0, (5, 5)), linewidth=1.5, label='Temperature Lower Bound', color='tab:grey')
            lines1[sensor] = line

        elif sensor == 'Actual Cooling Setpoint':
            line, = ax3.plot(time, value, '-.', linewidth=1.5, label='Temperature Upper Bound', color='tab:grey')
            lines1[sensor] = line

    if room in config["uncontrolled_rooms"]:
        controlled_room = config["uncontrolled_rooms"][room]
        title = f'Summary of {room} (vs. {controlled_room}) on {start_time.format("YYYY-MM-DD")}'
        filename = f'{path}/{room}(vs. {controlled_room}).pdf'
    else:
        title = f'Summary of {room} on {start_time.format("YYYY-MM-DD")}'
        filename = f'{path}/{room}.pdf'

    #########################
    # configure ax1 and ax3 #
    #########################
    lcolor = lines1['Actual Supply Flow'].get_color()
    ax1.set_ylabel('Airflow (CFM)', color=lcolor)
    ax1.tick_params(axis='y', labelcolor=lcolor, color=lcolor)

    if room == 'rm-4140':
        ax1.set_ylim(-20.0, 2673.4265)
        controlled_axes_range[room] = {'ax1':ax1.get_ylim()}
    elif room not in config["uncontrolled_rooms"]:
        ax1.set_ylim(ymin=-20)
        controlled_axes_range[room] = {'ax1':ax1.get_ylim()}
    else:
        ax1.set_ylim(controlled_axes_range[controlled_room]['ax1'])

    lcolor = lines1['Zone Temperature'].get_color()
    ax3.set_ylim(64, 81)
    ax3.tick_params(axis='y', labelcolor=lcolor, color=lcolor)
    ax3.set_ylabel('Temperature (F)', color=lcolor)
    ax3.yaxis.set_major_locator(MultipleLocator(5))

    ax1.xaxis.set_major_locator(hours)
    ax1.xaxis.set_major_formatter(hours_formatter)
    ax1.grid(True)

    lgd = ax1.legend(list(lines1.values()), [l.get_label() for l in lines1.values()], loc='center', bbox_to_anchor=(0.5, 1.19),
        fancybox=True, shadow=True, ncol=2)
    lgds.append(lgd)
    ax1.set_title(title,y=1.37)
    # -------

    if has_locals:
        # get_local_sensor_plot_details(axarr, lgds) # POSITIONING if needed
        ax2 = axarr[1] # axes for CO2
        ax4 = ax2.twinx() # axes for humidity

        lines2 = {} # lines on ax2 and ax4 (co2, humidity)

        ##################################       
        # read local sensors data & plot #
        ##################################
        with open(f'CO2_data/{room}/{str(start_time.date())}.csv') as csvFile:
            reader = csv.reader(csvFile, delimiter=',', quotechar='"')
            next(reader)
            time, co2, humidity = [], [], []
            for row in reader:
                t = arrow.get(row[0])
                if t < start_time:
                    continue
                time.append(t.datetime)
                co2.append(float(row[1]))
                humidity.append(float(row[2]))
            # co2
            line_co2, = ax2.plot(time, co2, linewidth=3, label='CO2 Density', color='tab:red')
            lines2["Carbon Dioxide Concentration"] = line_co2

            # humidity
            line_humidity, = ax4.plot(time, humidity, linewidth=3, label='Relative Humidity', color='tab:purple')
            lines2["Humidity"] = line_humidity

        lgd = ax1.legend(list(lines1.values()), [l.get_label() for l in lines1.values()], loc='lower center', bbox_to_anchor=(0.5, 0.98),
                        fancybox=True, shadow=True, ncol=2)
        lgds.append(lgd)
        ax1.set_title(title, y=1.43)

        #########################
        # configure ax2 and ax4 #
        #########################
        ax2.set_ylim(350,450)
        lcolor = lines2['Carbon Dioxide Concentration'].get_color()
        ax2.set_ylabel('CO2 Density (ppm)', color=lcolor)
        ax2.tick_params(axis='y', labelcolor=lcolor, color=lcolor, which='both')
        ax2.yaxis.set_minor_locator(AutoMinorLocator())

        # print(ax4.get_ylim())
        ax4.set_ylim(58.525, 71.575)
        lcolor = lines2['Humidity'].get_color()
        ax4.set_ylabel('Humidity (%)', color=lcolor)
        ax4.tick_params(axis='y', labelcolor=lcolor, color=lcolor)
        ax4.yaxis.set_major_locator(MultipleLocator(0.5))
        ax4.yaxis.set_major_locator(MultipleLocator(2))

        ax2.grid(True)

        lgd = ax2.legend(list(lines2.values()), [l.get_label() for l in lines2.values()], loc='lower center', bbox_to_anchor=(0.5, 0.98),
            fancybox=True, shadow=True, ncol=2)
        lgds.append(lgd)
        # ---------

    ########################
    # configure fig & save #
    ########################
    fig.autofmt_xdate()
    plt.savefig(filename, bbox_extra_artists=lgds, bbox_inches='tight')
    plt.close()
    
    
