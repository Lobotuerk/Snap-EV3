#!/usr/bin/env python3
from __future__ import print_function

import os
import sys
import urllib
import time

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import TouchSensor, ColorSensor, GyroSensor, UltrasonicSensor

import cgi
from http.server import HTTPServer, SimpleHTTPRequestHandler


BadRequest = 400
ServiceUnavailable = 503


class Ev3Handler(SimpleHTTPRequestHandler):

    devices = {}

    def do_GET(self):
        print(self.path)
        if self.path.startswith("/ev3/"):
            url = urllib.parse.urlparse(self.path)
            path = url.path.split("/")
            params = urllib.parse.parse_qs(url.query)
            #print(params)
            #print(params['portName'])
            #print(params['type'])
            if path[2] == "sensor":
                portN = params['portName'][0]
                #print("PORTN = " + str(portN))
                if portN == '1':
                    portN = INPUT_1
                elif portN == '2':
                    portN = INPUT_2
                elif portN == '3':
                    portN = INPUT_3
                elif portN == '4':
                    portN = INPUT_4
                type = params['type'][0]
                #print("TYPE = " + str(type))
                if type == 'touch':
                    #print("TouchSensor")
                    ts = TouchSensor(portN)
                    return self.send_result(ts.is_pressed)
                if type == 'color':
                    #print("ColorSensor")
                    ts = ColorSensor(portN)
                    return self.send_result(ts.reflected_light_intensity)
                if type == 'gyro':
                    #print("ColorSensor")
                    ts = GyroSensor(portN)
                    return self.send_result(ts.angle)
                if type == 'ultra':
                    #print("ColorSensor")
                    ts = UltrasonicSensor(portN)
                    return self.send_result(ts.distance_centimeters)
            if path[2] == "motor":
                portN = params['portName'][0]
                if portN == 'A':
                    portN = OUTPUT_A
                if portN == 'B':
                    portN = OUTPUT_B
                if portN == 'C':
                    portN = OUTPUT_C
                if portN == 'D':
                    portN = OUTPUT_D
                type = params['type'][0]
                if type == 'large':
                    motor = LargeMotor(portN)
                    if 'seconds' and 'speed' in params:
                        seconds = float(params['seconds'][0])
                        speed = float(params['speed'][0])
                        motor.on_for_seconds(SpeedPercent(speed), seconds)
                        return self.send_result("OK")
                    if 'rotations' and 'speed' in params:
                        rotations = float(params['rotations'][0])
                        speed = float(params['speed'][0])
                        motor.on_for_rotations(SpeedPercent(speed), rotations)
                        return self.send_result("OK")
                if type == 'medium':
                    motor = MediumMotor(portN)
                    if 'seconds' and 'speed' in params:
                        seconds = float(params['seconds'][0])
                        speed = float(params['speed'][0])
                        motor.on_for_seconds(SpeedPercent(speed), seconds)
                        return self.send_result("OK")
                    if 'rotations' and 'speed' in params:
                        rotations = float(params['rotations'][0])
                        speed = float(params['speed'][0])
                        motor.on_for_rotations(SpeedPercent(speed), rotations)
                        return self.send_result("OK")
            return self.send_result("ERROR")

        if self.path == "/":
            # Serve the main Snap! page instead of the directory listing
            self.path = "snap.html"
        SimpleHTTPRequestHandler.do_GET(self)


    def find_device(self, port, device_class):
        if port in Ev3Handler.devices:
            device = Ev3Handler.devices[port]
        else:
            device = ev3.Device(device_class, address=port)
            Ev3Handler.devices[port] = device
            print("New device object created, path = " + device._path)
        return device


    def send_result(self, value):
        value = str(value)
        self.send_response(200)
        self.send_header("Cache-control", "no cache")
        self.end_headers()
        self.wfile.write(value.encode("utf-8"))
        #self.wfile.write(b"\n")


    def error(self, code):
        self.send_response(code)
        self.send_header("Cache-control", "no cache")
        self.end_headers()


if __name__ == "__main__":
    port = 9000
    os.chdir(os.path.join(os.path.dirname(__file__), "snap"))
    server = HTTPServer(("", port), Ev3Handler)
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    try:
        print("Server Running")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % ("", port))
