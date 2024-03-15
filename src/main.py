import os
import json
import re
import cv2
import requests
from datetime import datetime

from image_downloading import download_image

file_dir = os.path.dirname(__file__)
prefs_path = os.path.join(file_dir, 'preferences.json')
default_prefs = {
        'url': 'https://tile.googleapis.com/v1/2dtiles/{z}/{x}/{y}',
        'session_url': 'https://tile.googleapis.com/v1/createSession',
        'api_key': '',
        'tile_size': 256,
        'channels': 3,
        'dir': os.path.join(file_dir, 'images'),
        'headers': {
            "Content-Type": "application/json"
        },
        'payload': {
            'mapType': 'satellite',
            'language': 'en-US',
            'region': 'US'
        },
        'tl': '',
        'br': '',
        'zoom': ''
    }


def take_input(messages):
    inputs = []
    print('Enter "r" to reset or "q" to exit.')
    for message in messages:
        inp = input(message)
        if inp == 'q' or inp == 'Q':
            return None
        if inp == 'r' or inp == 'R':
            return take_input(messages)
        inputs.append(inp)
    return inputs

def get_sessionId(url, payload, headers, key):
    response = requests.post(url, json=payload, headers=headers, params={"key": key})

    if response.status_code == 200:
        session_id = response.json()["session"]
        print("Session ID:", session_id)
        return session_id
    else:
        print("Failed to create session. Status code:", response.status_code)

def run():
    with open(os.path.join(file_dir, 'preferences.json'), 'r', encoding='utf-8') as f:
        prefs = json.loads(f.read())

    if not os.path.isdir(prefs['dir']):
        os.mkdir(prefs['dir'])

    if (prefs['tl'] == '') or (prefs['br'] == '') or (prefs['zoom'] == ''):
        messages = ['Top-left corner: ', 'Bottom-right corner: ', 'Zoom level: ']
        inputs = take_input(messages)
        if inputs is None:
            return
        else:
            prefs['tl'], prefs['br'], prefs['zoom'] = inputs

    lat1, lon1 = re.findall(r'[+-]?\d*\.\d+|d+', prefs['tl'])
    lat2, lon2 = re.findall(r'[+-]?\d*\.\d+|d+', prefs['br'])

    zoom = int(prefs['zoom'])
    channels = int(prefs['channels'])
    tile_size = int(prefs['tile_size'])
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    session_id = get_sessionId(prefs['session_url'], prefs['payload'], prefs['headers'], prefs['api_key'])

    params = {
        'key': prefs['api_key'],
        'session': session_id
    }

    img = download_image(lat1, lon1, lat2, lon2, zoom, prefs['url'],
        params, tile_size, channels)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name = f'img_{timestamp}.png'
    cv2.imwrite(os.path.join(prefs['dir'], name), img)
    print(f'Saved as {name}')


if os.path.isfile(prefs_path):
    run()
else:
    with open(prefs_path, 'w', encoding='utf-8') as f:
        json.dump(default_prefs, f, indent=2, ensure_ascii=False)

    print(f'Preferences file created in {prefs_path}')
