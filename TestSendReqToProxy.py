import requests
from requests.compat import urljoin


def api_post(base_url, api, parameters):
    api_endpoint = urljoin(base_url, api)
    headers = {'Content-Type': 'application/json',
               'X-Device-Name':'Arduino Furnace Monitor'}
    post = requests.post(url=api_endpoint, headers=headers, json=parameters)
    return post


base_url = 'http://192.168.0.10:8080'
api = 'iot-redirect/data/add/'

data = {'tag': 'AcComp001',
        'value': 'On',
        }

r = api_post(base_url, api, data)
print('Status:', r.status_code)
print('Reason:', r.reason)
print('Response text:', r.text)
