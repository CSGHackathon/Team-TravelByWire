#!/usr/bin/env python
from flask import *

app = Flask(__name__)

light_states = {
    "projector": True,
    "light1": False,
    "light2": False
}

@app.route('/')
def index():
    return render_template("index.html", **light_states)

@app.route('/js/<remainder>',methods=['GET'])
@app.route('/img/<remainder>',methods=['GET'])
@app.route('/css/<remainder>',methods=['GET'])
def get_static(remainder):
    return send_from_directory(app.static_folder,request.path[1:])

if __name__ == "__main__":
    app.run(host="0.0.0", debug=True)
