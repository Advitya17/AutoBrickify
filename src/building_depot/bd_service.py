'''
bd_service.py
~~~~~~


@copyright: (c) 2013 SynergyLabs
@license:   UCSD License. See License file for details.
'''
import requests
import json
from functools import wraps


def _validate_response(r):
    if r.status_code // 100 != 2:
        raise BDError(r)


def _request_wrapper(func):

    @wraps(func)
    def wrapper(arg, *args, **kwargs):
        if 'json_data' in kwargs:
            # if there is json data, parse the data to json
            kwargs['data'] = json.dumps(kwargs['json_data'])
            kwargs.pop('json_data')
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            kwargs['headers']['Content-Type'] = 'application/json'
        r = func(arg, *args, **kwargs)
        _validate_response(r)
        return r

    return wrapper


class BDCustomError(BaseException):

    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return 'Error: %d' % self.status_code


class BDError(BaseException):

    def __init__(self, response=None):
        if response is None:
            return
        self.status_code = response.status_code
        self.msg = {}
        try:
            r = response.json()
            for key, value in r.items():
                key, value = str(key), str(value)
                self.msg[key] = value
        except ValueError:
            self.msg = response.text

    def __str__(self):
        prt = ['status code: %d' % self.status_code]
        if type(self.msg) == dict:
            for key, value in self.msg.items():
                prt.append('%s: %s' % (key, value))
        else:
            prt.append(self.msg)
        return '\n'.join(prt)


class BuildingDepotService(object):

    def __init__(self, base_url, username, api_key,
                 auth_token=None, expiration=None, verify=False):
        self.base_url = base_url
        self.username = username
        self.api_key = api_key
        self.auth_token = auth_token
        self.expiration = expiration
        self.verify = verify

    @property
    def _init_headers(self):
        headers = {
            'X-BD-Api-Key': self.api_key,
            'Accept': 'application/json; charset=utf-8',
            'X-BD-Auth-Token': 'test',

        }
        if self.auth_token is not None:
            headers['X-BD-Auth-Token'] = self.auth_token
        return headers

    @property
    def _auth(self):
        return (self.username, self.api_key)

    @_request_wrapper
    def get(self, *args, **kwargs):
        self._preprocess_arg(args, kwargs)
        return requests.get(*args, **kwargs)

    @_request_wrapper
    def post(self, *args, **kwargs):
        self._preprocess_arg(args, kwargs)
        return requests.post(*args, **kwargs)

    @_request_wrapper
    def put(self, *args, **kwargs):
        self._preprocess_arg(args, kwargs)
        return requests.put(*args, **kwargs)

    @_request_wrapper
    def delete(self, *args, **kwargs):
        self._preprocess_arg(args, kwargs)
        return requests.delete(*args, **kwargs)

    def _preprocess_arg(self, args, kwargs):
        kwargs['verify'] = self.verify
