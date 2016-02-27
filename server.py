#!/usr/bin/env python

import json
import logging
import sys
import threading
import time

from util import *

from flask import *

import requests

app = Flask(__name__)

PROJECTOR_URL_POWER = "http://raspberrycake.lan/SEND_ONCE/projector.conf/KEY_POWER"
PROJECTOR_URL_STATUS = "http://yesbot.lan"

LIGHT1_URL_ON = "http://localhost:8000"
LIGHT1_URL_OFF = "http://localhost:8000"

LIGHT2_URL_ON = "http://localhost:8000"
LIGHT2_URL_OFF = "http://localhost:8000"

device_states = {
    "projector": {
        "state": False,
        "on": lambda: requests.get(PROJECTOR_URL_POWER),
        "off": lambda: requests.get(PROJECTOR_URL_POWER),
        "is_on": lambda: get(PROJECTOR_URL_STATUS, 1).status_code == 200
    }, "light1": {
        "state": False,
        "on": lambda: requests.get(LIGHT1_URL_ON),
        "off": lambda: request.get(LIGHT1_URL_OFF),
        "is_on": lambda: False
    }, "light2": {
        "state": False,
        "on": lambda: requests.get(LIGHT2_URL_ON),
        "off": lambda: request.get(LIGHT2_URL_OFF),
        "is_on": lambda: False
    }
}

@app.route('/')
def index():
    refresh_states()
    target_device = new_state = None

    if 'device' in request.args:
        target_device = request.args['device']
    if 'state' in request.args:
        new_state = request.args['state']

    if target_device is not None and new_state is not None:
        if target_device in device_states:
            device_states[target_device][new_state]()

        device_states[target_device]['state'] = device_states[target_device]['is_on']()

    return render_template("index.html", **device_states)


def refresh_states():
    for device in device_states:
        device_states[device]['state'] = device_states[device]["is_on"]()

@app.route("/status")
def status():
    return json.dumps({ x:y['state'] for x, y in device_states.items() })


@app.route('/js/<remainder>',methods=['GET'])
@app.route('/img/<remainder>',methods=['GET'])
@app.route('/css/<remainder>',methods=['GET'])
def get_static(remainder):
    return send_from_directory(app.static_folder,request.path[1:])

def start_fetching_states():
    def fetch_states():
        print("Fetching states")
        threading.Timer(3.0, fetch_states).start()
        refresh_states()
    fetch_states()

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    print("server up")
    start_fetching_states()
    app.run(host="0.0.0", debug=True)
