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

action_pairs = []

if_conditions = []
then_actions = {}

for device in device_states :
    then_actions[device+"_on"] = device_states[device]["on"]
    then_actions[device+"_off"] = device_states[device]["off"]
    then_actions[device+"_toggle"] = lambda : device_states[device]["off"] if device_states[device]["state"] else device_states[device]["off"]
    if_conditions.append(device+"_on")
    if_conditions.append(device+"_off")

def send_event(evtname) :
    print("EVENT !"+evtname)
    for x in action_pairs :
        if x[0] == evtname :
            then_actions[x[1]]()

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

    return render_template("index.html", devices=device_states, ifthens=action_pairs, ifs=if_conditions, thens=then_actions.keys())


@app.route('/addifthen',methods=["POST"])
def addifthen():
    print(request.form)
    action_pairs.append((request.form['if'],request.form['then']))
    return redirect('/')
@app.route('/removeifthen',methods=["GET"])
def removeifthen():
    for x in action_pairs :
        if x[0] == request.args["if"] and x[1] ==request.args["then"] :
            action_pairs.remove(x)
            break
    return redirect('/')

def refresh_states():
    for device in device_states:
        prev = device_states[device]['state'] 
        new = device_states[device]['state'] = device_states[device]["is_on"]()
        if prev and not new :
            send_event(device+"_off")
        elif new and not prev :
            send_event(device+"_on")

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
