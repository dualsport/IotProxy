# Simple IOT Proxy Server
# Forwards POST calls with JSON payloads ONLY
# Returns server respons to client
# Client device POSTs to proxy IP as follows:
#  '192.168.0.99:8080/redirect-site-code/api/endpoint/' + json data
# Proxy replaces 'redirect-site-code' with actual site address from lookup
#  'https://actual-site/api/endpoint/' + json data
# Proxy replies to client with reply from server
# Each request received starts new thread to handle connection
# Proxy is supplies authentication to server

# Todo: Handle internet outage - Store request locally, return 202 Accepted to client


import socket
import sys
import os
import threading
import json
from time import sleep
import requests
from urllib.parse import urljoin
import datetime
import email
import io
import settings


host = os.getenv('HOST', '192.168.0.10')
listening_port = int(os.getenv('LISTENING_PORT', '8080'))
max_conn = int(os.getenv('MAX_CONN', '5'))
buffer_size = int(os.getenv('BUFFER_SIZE', '4096'))


def handle_connect(conn, addr, data):
    print(f'Handling connection...{datetime.datetime.now()}')
    first_line = data.split('\n')[0]
    method = first_line.split(' ')[0]
    req_url = first_line.split(' ')[1]
    # split to drop json then and again to drop url parts leaving only headers
    headers_only = data.split('\r\n\r\n')[0].split('\r\n',1)[1]
    # convert to headers as a dict
    headers = dict(email.message_from_file(io.StringIO(headers_only)))
    target = forward_to(req_url, headers)
    jsn = parse_json(data)
    if method != 'POST':
        client_response = 'HTTP/1.0 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nMethod ' + method + ' not allowed\r\n'
    elif 'Error' in target:
        client_response = 'HTTP/1.0 400 Bad Request\r\nContent-Type: text/plain\r\n\r\n' + target['Error'] + '\r\n'
    elif 'Error' in jsn:
        client_response = 'HTTP/1.0 400 Bad Request\r\nContent-Type: text/plain\r\n\r\n' + jsn['Error'] + '\r\n'
    else:
        srv_response = api_post(target['base'],
                                target['endpoint'],
                                target['token'],
                                jsn)
        client_response = 'HTTP/1.0 ' + str(srv_response.status_code) + ' '
        client_response += srv_response.reason + '\r\n'
        client_response += 'Content-Type: ' + srv_response.headers['Content-Type']
        client_response += '\r\n\r\n' + srv_response.content.decode('ASCII') + '\r\n'
    conn.send(client_response.encode('ascii'))
    conn.close()
    print(f'Done handling connection. {datetime.datetime.now()}\n')


def forward_to(req_url, req_headers):
    try:
        device = req_headers['X-Device-Name']
    except KeyError:
        return {'Error': 'X-Device-Name request header is missing'}
    try:
        site = settings.device_sites[device]
    except KeyError:
        return {'Error': 'No site defined for device'}
    base_url = settings.redirect_sites[site]['url']
    token = settings.redirect_sites[site]['token']

    url_parts = [i for i in req_url.split('/') if i]
    endpoint = '/'.join(url_parts[1:]) + '/'
    return {'base': base_url,
            'endpoint': endpoint,
            'token': token
           }


def parse_json(req_data):
    # Returns valid JSON from request
    json_beg = req_data.find('{')
    json_end = req_data.rfind('}') + 1

    if json_beg > 0 and json_end > 0:
        try:
            parsed_data = json.loads(req_data[json_beg:json_end])
        except json.decoder.JSONDecodeError:
            return {'Error': 'Invalid JSON'}
    else:
        return {'Error': 'JSON not found'}
    return parsed_data


def api_post(base_url, api, token, parameters):
    # Post to api endpoint
    api_endpoint = urljoin(base_url, api)
    headers = {'Host': base_url.split('//')[1],
               'Content-Type': 'application/json',
               'Authorization': token,
              }
    post = requests.post(url=api_endpoint, headers=headers, json=parameters)
    return post


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Initiate socket
    s.bind((host, listening_port))  # Bind socket for listening
    s.listen(max_conn)  # Start listening
    print(f'Listening on: {host}:{listening_port}')
    while True:
        conn, addr = s.accept()  # Accept incoming client connection
        conn.settimeout(1)
        data = ''
        print(f'New connection. {datetime.datetime.now().time()}')
        while True:
            try:
                new_data = conn.recv(buffer_size)  # Receive data
                if not new_data:
                    break
                print(f'New data: {new_data}')
                data += new_data.decode(encoding='UTF-8',errors='strict')
            except socket.timeout:
                break
        threading.Thread(target=handle_connect, args=(conn, addr, data)).start()
