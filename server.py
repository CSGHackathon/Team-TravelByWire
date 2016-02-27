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

action_pairs = []

if_conditions = []
then_actions = {}

for device in device_actions :
    then_actions[device+"_on"] = device_actions[device]["on"]
    then_actions[device+"_off"] = device_actions[device]["off"]
    then_actions[device+"_toggle"] = lambda : device_actions[device]["off"] if device_actions[device]["state"] else device_actions[device]["off"]
    if_conditions.append(device+"_on")
    if_conditions.append(device+"_off")

def send_event(evtname) :
    print("EVENT !"+evtname)
    for x in action_pairs :
        if x[0] == evtname :
            then_actions[x[1]]()

@app.route('/')
def index():
    return render_template("index.html", devices=device_actions, ifthens=action_pairs, ifs=if_conditions, thens=then_actions.keys())

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
    old_states = get_state()
    new_states = {}
    for device in device_actions:
        new_states[device] = device_actions[device]["is_on"]()
        if old_states[device] and not new_states[device] :
            send_event(device+"_off")
        if not old_states[device] and new_states[device] :
            send_event(device+"_on")
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

    with open("states.json", 'w+') as f:
        json.dump(init_states, f)

    logging.basicConfig(level=logging.ERROR)
    start_fetching_states()


if __name__ == "__main__":
    _setup()
    print("server up")
    app.run(host="0.0.0.0", debug=True)
