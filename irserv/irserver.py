#!/usr/bin/env python
import BaseHTTPServer
import subprocess
import json
import RPi.GPIO as gpio
from threading import Timer

gpio.setmode(gpio.BOARD)
gpio.setup(12, gpio.OUT)

pin = gpio.PWM(12, 1200)

def stopbuzz():
    pin.stop()

class Handler(BaseHTTPServer.BaseHTTPRequestHandler) :
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
    def do_GET(self):
        path = self.requestline.split()[1]
        components = filter(lambda x : x != "",path.split("/"))
        print(components)
        subprocess.call(["irsend"]+components)
        pin.start(1)
        Timer(.25, stopbuzz, ()).start()
        self.send_response(200)
        self.end_headers()


server = BaseHTTPServer.HTTPServer(("0.0.0.0",80),Handler)

try :
    server.serve_forever()
except KeyboardInterrupt :
    pass
server.server_close()
gpio.cleanup()
