from building_depot.data_service import DataService
from building_depot.bd_service import BDCustomError
from datetime import datetime
from dateutil import parser
from dateutil.tz import tzlocal
import json


class Sensor(object):

    def __init__(self,
                 service=None,
                 uuid=None,
                 created_time=None,
                 source_name=None,
                 template=None,
                 owner=None,
                 uri=None,
                 source_identifier=None,
                 network=None,
                 contexts=None,
                 **kwargs):
        self.service = None
        self.uuid = uuid
        self.source_name = source_name
        self.source_identifier = source_identifier
        self.template = template
        self.network = network
        self.contexts = {} if contexts is None else contexts
        self.created_time = created_time
        self.owner = owner
        self.uri = uri


class DataPoint(object):

    def __init__(self, sensor, sensor_point, dp_dict):
        self.time, self.value = dp_dict.items()[0]
        self.time = parser.parse(self.time)
        self.raw = dp_dict
        self.sensor = sensor
        self.sensor_point = sensor_point

    def json(self):
        js = self.value.replace("\',", "\",")\
                       .replace("\'\}", "\"\}")\
                       .replace("\'\:", "\"\:")\
                       .replace("u\'", "\"")\
                       .replace("\'", "\"")
        return json.loads(js)


class SensorService(object):
    '''Service build on top of DataService'''

    def __init__(self, data_service_url, username, api_key):
        self.url = data_service_url
        self.service = DataService(data_service_url,
                                   username=username,
                                   api_key=api_key)

    def get_sensor(self, context):
        rt = self.service.list_sensors(context, offset=0, limit=2)
        sensors = rt['sensors']
        if len(sensors) == 0:
            raise BDCustomError(404)
        return Sensor(service=self, **sensors[0])

    def query_sensors(self, context):
        sensor_fetched = 0
        while True:
            rt = self.service.list_sensors(context, offset=sensor_fetched)
            sensors = rt['sensors']
            for sensor_dict in sensors:
                yield Sensor(service=self, **sensor_dict)
            sensor_fetched += len(sensors)
            if rt['total'] == sensor_fetched:
                break

    def get_sensor_by_uuid(self, uuid):
        info = self.service.view_sensor(uuid)
        return Sensor(service=self, **info)

    def create_sensor(self, sensor):
        uuid = self.service.create_sensor(
            source_name=sensor.source_name,
            source_identifier=sensor.source_identifier,
            template=sensor.template,
            network=sensor.network,
            context=sensor.contexts)
        sensor.uuid = uuid
        sensor.service = self

    def delete_sensor(self, sensor):
        self.service.delete_sensor(sensor.uuid)

    def read_latest_datapoint(self, sensor, sensor_point):
        rt = self.service.get_latest_timeseries_datapoint(sensor.uuid,
                                                          sensor_point)
        data = [DataPoint(sensor, sensor_point, dp) for dp in rt['timeseries']
                if dp is not None]
        if len(data) == 0:
            raise BDCustomError(404)
        return data[0], rt['span']

    def read_datapoints(self, sensor, sensor_point, start, end):
        rt = self.service.get_timeseries_datapoints(sensor.uuid, sensor_point,
                                                    start, end)
        data = [DataPoint(sensor, sensor_point, dp) for dp in rt['timeseries']
                if dp is not None]
        return data, rt['span']

    def read_first_datapoint(self, sensor, sensor_point, start, end):
        data, _ = self.read_datapoints(sensor, sensor_point, start, end)
        if len(data) == 0:
            raise BDCustomError(404)
        return data[0]

    def read_last_datapoint(self, sensor, sensor_point, start, end):
        data, _ = self.read_datapoints(sensor, sensor_point, start, end)
        if len(data) == 0:
            raise BDCustomError(404)
        return data[-1]

    def read_latest_datapoints_batch(self, sensors, sensor_points_list):
        if type(sensor_points_list) is str:
            sensor_points = (sensor_points_list,)
            sensor_sp_zip = ((sensor, sensor_points) for sensor in sensors)
        else:
            sensor_sp_zip = zip(sensors, sensor_points_list)
        batch_query = {}
        sensor_dict = {}
        for sensor, sp_names in sensor_sp_zip:
            batch_query[sensor.uuid] = {
                sp_name: {
                    'start': None,
                    'end': None,
                }
                for sp_name in sp_names
            }
            sensor_dict[sensor.uuid] = sensor
        rt = self.service.get_timeseries_datapoints_batch(batch_query)
        rt_dps = {}
        for uuid, data in rt.items():
            if 'message' in data:
                raise BDCustomError(404)
            rt_dps[uuid] = {
                spname: DataPoint(sensor_dict[uuid], spname, dp_raw['timeseries'][-1])
                for spname, dp_raw in data.items()
                if len(dp_raw['timeseries']) > 0
            }
        return rt_dps

    def read_sensor_latest_datapoints_batch(self, sensor, sp_names):
        if type(sp_names) == str:
            sp_names = (sp_names,)
        rt = self.read_latest_datapoints_batch((sensor,), (sp_names,))
        return rt[sensor.uuid]

    def write_datapoint(self, sensor, sensor_point, *datapoints):
        self.service.put_timeseries_datapoints(sensor.uuid, sensor_point,
                                               list(datapoints))

    def write_datapoint_now(self, sensor, sensor_point, datapoint):
        timestamp = datetime.now(tzlocal()).isoformat()
        self.write_datapoint(sensor, sensor_point, {
            timestamp: datapoint,
        })

    def write_datapoint_now_json(self, sensor, sensor_point, datapoint):
        self.write_datapoint_now(sensor, sensor_point, json.dumps(datapoint))

    def create_sensorpoint(self, sensor, **data):
        self.service.create_sensorpoint(sensor.uuid, **data)

    def list_sensorpoints(self, sensor):
        sensor_point_fetched = 0
        while True:
            rt = self.service.list_sensorpoints(sensor.uuid,
                                                offset=sensor_point_fetched)
            sps = rt['sensorpoints']
            for sp in sps:
                yield sp
            sensor_point_fetched += len(sps)
            if rt['total'] == sensor_point_fetched:
                break

    def list_sensor_context(self, sensor):
        context_fetched = 0
        while True:
            rt = self.service.list_sensor_context(sensor.uuid,
                                                  offset=context_fetched)
            contexts = rt['contexts']
            for context in contexts:
                yield {context['keyword']: context['tag']}
            context_fetched += len(contexts)
            if rt['total'] == context_fetched:
                break
