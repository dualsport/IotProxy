import requests
from requests.compat import urljoin


def api_get(base_url, api, token, parameters=None):
    api_endpoint = 'http://' + base_url + '/' + api
    headers = {'Content-Type': 'application/json',
               }

    r = requests.get(url=api_endpoint, headers=headers, params=parameters)


def api_post(base_url, api, parameters):
    api_endpoint = urljoin(base_url, api)
    headers = {'Content-Type': 'application/json',
               }
    post = requests.post(url=api_endpoint, headers=headers, json=parameters)
    return post


base_url = 'http://192.168.0.10:8080'
api = 'iot-stg-redirect/data/add/'

data = {'tag': 'test_integer',
        'value': '127',
        }

r = api_post(base_url, api, data)
print('Status:', r.status_code)
print('Reason:', r.reason)
print('Response text:', r.text)
