import socket
import sys
import threading
import json
from time import sleep
import requests
from urllib.parse import urljoin


host = ''
listening_port = 8080
max_conn = 5
buffer_size = 4096
redirect_sites = {'iot-stg-redirect': 'https://iot-stg.redcatmfg.com/',
                  'iot-redirect': 'https://iot.redcatmfg.com'}
tokens = {'https://iot-stg.redcatmfg.com/': 'Token d9bcbcc509f360b46684f86ca4532e66562dac66',
          'https://iot.redcatmfg.com': 'Token a0444fc04865a861fb5dc291f50483264e74a8a6'}


def handle_connect(conn, addr, data):
    # print(f'addr: {addr}')  # Return address
    first_line = data.split('\n')[0]
    method = first_line.split(' ')[0]
    url_parts = parse_url(first_line.split(' ')[1])
    jsn = parse_json(data)
    if method != 'POST':
        response = 'HTTP/1.0 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nMethod ' + method + ' not allowed\r\n'
    elif 'Error' in url_parts:
        response = 'HTTP/1.0 400 Bad Request\r\nContent-Type: text/plain\r\n\r\n' + url_parts['Error'] + '\r\n'
    elif 'Error' in jsn:
        response = 'HTTP/1.0 400 Bad Request\r\nContent-Type: text/plain\r\n\r\n' + jsn['Error'] + '\r\n'
    else:
        response = 'HTTP/1.0 202 Accepted\r\nContent-Type: text/plain\r\n\r\nAccepted\r\n'
    conn.send(response.encode('ascii'))
    conn.close()
    print(addr, url_parts, jsn)
    tries = 0
    while tries < 3:
        post_response = fwd_post(url_parts['base'], url_parts['endpoint'],
                                 tokens[url_parts['base']], jsn)
        print(f'Response code: {post_response.status_code}')
        print(post_response.request.headers)
        print(post_response.request.body)
        print(f'Response content: {post_response.content}\n')

        if int(int(post_response.status_code) / 100) == 2:
            break
        else:
            # Post call failed
            sleep(5)
            tries += 1


def parse_url(url):
    # Split & remove empty strings
    url_parts = [i for i in url.split('/') if i]
    target = url_parts[0]
    if target in redirect_sites:
        base = redirect_sites[target]
    else:
        return {'Error': 'Redirect target does not exist'}
    return {'base': base,
            'endpoint': '/'.join(url_parts[1:])
           }
 

def parse_json(req_data):
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


def fwd_post(base_url, api, token, parameters):
    api_endpoint = urljoin(base_url, api)
    headers = {'Content-Type': 'application/json',
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
