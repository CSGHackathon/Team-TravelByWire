#!/usr/bin/env python

import json
import logging
import pickle
import sys
import threading
import time

from util import *

from flask import *

import requests

app = Flask(__name__)

PROJECTOR_URL_POWER = "http://raspberrycake.lan/SEND_ONCE/projector.conf/KEY_POWER"
PROJECTOR_URL_STATUS = "http://yesbot.lan"

LIGHT1_URL_ON = "http://tinylamp/on"
LIGHT1_URL_OFF = "http://tinylamp/off"
LIGHT1_URL_STATUS = "http://tinylamp.lan"

LIGHT2_URL_ON = "http://localhost:8000"
LIGHT2_URL_OFF = "http://localhost:8000"

device_actions = {
    "projector": {
        "on": lambda: requests.get(PROJECTOR_URL_POWER),
        "off": lambda: requests.get(PROJECTOR_URL_POWER),
        "is_on": lambda: get(PROJECTOR_URL_STATUS, 1).status_code == 200
    }, "light1": {
        "on": lambda: requests.get(LIGHT1_URL_ON),
        "off": lambda: requests.get(LIGHT1_URL_OFF),
        "is_on": lambda: get(LIGHT1_URL_STATUS, 1).text == "on"
    }, "light2": {
        "on": lambda: requests.get(LIGHT2_URL_ON),
        "off": lambda: request.get(LIGHT2_URL_OFF),
        "is_on": lambda: False
    }
}


@app.route('/')
def index():
    return render_template("index.html", devices=device_actions)

@app.route('/toggle')
def toggle():
    if 'device' in request.args:
        target_device = request.args['device']
    if 'state' in request.args:
        new_state = request.args['state']

    if target_device is not None and new_state is not None:
        if target_device in device_actions:
            print("Turning {} {}".format(target_device, new_state))
            device_actions[target_device][new_state]()
    return ""

def refresh_states():
    new_states = {}
    for device in device_actions:
        new_states[device] = device_actions[device]["is_on"]()
    save_state(new_states)

@app.route("/status")
def status():
    with open("states.json") as f:
        return "".join(f.readlines())


@app.route('/js/<remainder>',methods=['GET'])
@app.route('/img/<remainder>',methods=['GET'])
@app.route('/css/<remainder>',methods=['GET'])
def get_static(remainder):
    return send_from_directory(app.static_folder,request.path[1:])

def start_fetching_states():
    def fetch_states():
        threading.Timer(1.0, fetch_states).start()
        refresh_states()
    fetch_states()

def get_state():
    with open("states.json") as f:
        return json.load(f)

def save_state(states):
    with open("states.json", "w+") as f:
        json.dump(states, f)

def _setup():
    init_states = {
        "projector": False,
        "light1": False,
        "light2": False,
    }

    logging.basicConfig(level=logging.ERROR)
    start_fetching_states()

    with open("states.json", 'w+') as f:
        json.dump(init_states, f)


if __name__ == "__main__":
    _setup()
    print("server up")
    app.run(host="0.0.0.0", debug=True)
