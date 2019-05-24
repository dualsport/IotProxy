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
import settings as s


host = os.getenv('HOST', '')
listening_port = int(os.getenv('LISTENING_PORT'))
max_conn = int(os.getenv('MAX_CONN'))
buffer_size = int(os.getenv('BUFFER_SIZE'))
redirect_sites = s.redirect_sites


def handle_connect(conn, addr, data):
    first_line = data.split('\n')[0]
    method = first_line.split(' ')[0]
    url_parts = parse_url(first_line.split(' ')[1])
    jsn = parse_json(data)
    if method != 'POST':
        client_response = 'HTTP/1.0 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nMethod ' + method + ' not allowed\r\n'
    elif 'Error' in url_parts:
        client_response = 'HTTP/1.0 400 Bad Request\r\nContent-Type: text/plain\r\n\r\n' + url_parts['Error'] + '\r\n'
    elif 'Error' in jsn:
        client_response = 'HTTP/1.0 400 Bad Request\r\nContent-Type: text/plain\r\n\r\n' + jsn['Error'] + '\r\n'
    else:
        srv_response = api_post(url_parts['base'],
                                url_parts['endpoint'],
                                redirect_sites[url_parts['target']]['token'],
                                jsn)

        client_response = 'HTTP/1.0 ' + str(srv_response.status_code) + ' '
        client_response += srv_response.reason + '\r\n'
        client_response += 'Content-Type: ' + srv_response.headers['Content-Type']
        client_response += '\r\n\r\n' + srv_response.content.decode('ASCII') + '\r\n'
    conn.send(client_response.encode('ascii'))
    conn.close()


def parse_url(url):
    # Returns base url and api endpoint
    url_parts = [i for i in url.split('/') if i]
    target = url_parts[0]
    if target in redirect_sites:
        base = redirect_sites[target]['url']
    else:
        return {'Error': 'Redirect target does not exist'}
    return {'target': target,
            'base': base,
            'endpoint': '/'.join(url_parts[1:]) + '/'
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

    while True:
        conn, addr = s.accept()  # Accept incoming client connection
        data = conn.recv(buffer_size).decode()  # Receive data
        threading.Thread(target=handle_connect, args=(conn, addr, data)).start()
