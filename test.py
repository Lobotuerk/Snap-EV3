#!/usr/bin/env python3
from __future__ import print_function

import os
import sys
import urllib
import time

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent, MoveTank
from ev3dev2.display import Display
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.button import Button
from ev3dev2.led import Leds
from ev3dev2.sensor.lego import TouchSensor, ColorSensor, GyroSensor, UltrasonicSensor

import cgi
import ev3dev2.fonts as fonts
from http.server import HTTPServer, SimpleHTTPRequestHandler


BadRequest = 400
ServiceUnavailable = 503


class Ev3Handler(SimpleHTTPRequestHandler):

    devices = {}

    def do_GET(self):
        #print(self.path)
        if self.path.startswith("/ev3/"):
            url = urllib.parse.urlparse(self.path)
            path = url.path.split("/")
            params = urllib.parse.parse_qs(url.query)
            if path[2] == "sensor":
                if type == 'bt_left':
                    ts = Button()
                    return self.send_result(ts.left)
                if type == 'bt_right':
                    ts = Button()
                    return self.send_result(ts.right)
                if type == 'bt_up':
                    ts = Button()
                    return self.send_result(ts.up)
                if type == 'bt_down':
                    ts = Button()
                    return self.send_result(ts.down)
                if type == 'bt_enter':
                    ts = Button()
                    return self.send_result(ts.enter)
                portN = params['portName'][0]
                if portN == '1':
                    portN = INPUT_1
                elif portN == '2':
                    portN = INPUT_2
                elif portN == '3':
                    portN = INPUT_3
                elif portN == '4':
                    portN = INPUT_4
                type = params['type'][0]
                if type == 'touch':
                    ts = TouchSensor(portN)
                    return self.send_result(ts.is_pressed)
                if type == 'light':
                    ts = ColorSensor(portN)
                    return self.send_result(ts.reflected_light_intensity)
                if type == 'color':
                    ts = ColorSensor(portN)
                    return self.send_result(ts.color)
                if type == 'ambient':
                    ts = ColorSensor(portN)
                    return self.send_result(ts.ambient_light_intensity)
                if type == 'gyro':
                    ts = GyroSensor(portN)
                    return self.send_result(ts.angle)
                if type == 'ultra':
                    ts = UltrasonicSensor(portN)
                    return self.send_result(ts.distance_centimeters)
            if path[2] == "tank":
                port1 = params['port1'][0]
                if port1 == 'A':
                    port1 = OUTPUT_A
                if port1 == 'B':
                    port1 = OUTPUT_B
                if port1 == 'C':
                    port1 = OUTPUT_C
                if port1 == 'D':
                    port1 = OUTPUT_D
                port2 = params['port2'][0]
                if port2 == 'A':
                    port2 = OUTPUT_A
                if port2 == 'B':
                    port2 = OUTPUT_B
                if port2 == 'C':
                    port2 = OUTPUT_C
                if port2 == 'D':
                    port2 = OUTPUT_D
                motor = MoveTank(port1, port2)
                rotations = float(params['rotations'][0])
                speed1 = float(params['speed1'][0])
                speed2 = float(params['speed2'][0])
                motor.on_for_rotations(speed1, speed2, rotations)
                return self.send_result("OK")
            if path[2] == "led":
                led = Leds()
                type = params['type'][0]
                red = float(params['red'][0])
                green = float(params['green'][0])
                if green < 0:
                    green = 0
                if green > 100:
                    green = 100
                if red < 0:
                    red = 0
                if red > 100:
                    red = 100
                green = green / 100
                red = red / 100
                if type == 'left':
                    led.set_color('LEFT', (red,green))
                if type == 'right':
                    led.set_color('RIGHT', (red,green))
                return self.send_result("OK")

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
                #print(params)
                if type == 'large':
                    motor = LargeMotor(portN)
                    if 'seconds' in params and 'speed' in params:
                        seconds = float(params['seconds'][0])
                        speed = float(params['speed'][0])
                        motor.on_for_seconds(SpeedPercent(speed), seconds)
                        return self.send_result("OK")
                    if 'rotations' in params and 'speed' in params:
                        rotations = float(params['rotations'][0])
                        speed = float(params['speed'][0])
                        motor.on_for_rotations(SpeedPercent(speed), rotations)
                        return self.send_result("OK")
                    if 'run' in params and 'speed' in params:
                        speed = float(params['speed'][0])
                        if params['run'][0] == 'true':
                            motor.on(SpeedPercent(speed))
                        else:
                            motor.off()
                        return self.send_result("OK")
                if type == 'medium':
                    motor = MediumMotor(portN)
                    if 'seconds' in params and 'speed' in params:
                        seconds = float(params['seconds'][0])
                        speed = float(params['speed'][0])
                        motor.on_for_seconds(SpeedPercent(speed), seconds)
                        return self.send_result("OK")
                    if 'rotations' in params and 'speed' in params:
                        rotations = float(params['rotations'][0])
                        speed = float(params['speed'][0])
                        motor.on_for_rotations(SpeedPercent(speed), rotations)
                        return self.send_result("OK")
            return self.send_result("ERROR")

        if self.path == "/":
            self.path = "snap.html"
        SimpleHTTPRequestHandler.do_GET(self)


    def find_device(self, port, device_class):
        if port in Ev3Handler.devices:
            device = Ev3Handler.devices[port]
        else:
            device = ev3.Device(device_class, address=port)
            Ev3Handler.devices[port] = device
            #print("New device object created, path = " + device._path)
        return device


    def send_result(self, value):
        d = Display()
        d.text_grid("Robotica \neducativa \n    UTN FRT", font='luBS24')
        d.update()
        value = str(value)
        self.send_response(200)
        self.send_header("Cache-control", "no cache")
        self.end_headers()
        self.wfile.write(value.encode("utf-8"))


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
        #print("Server Running")
        d = Display()
        d.text_grid("Robotica \neducativa \n    UTN FRT", font='luBS24')
        d.update()
        led = Leds()
        led.set_color('LEFT',(0,0))
        led.set_color('RIGHT',(0,0))
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    #print(time.asctime(), "Server Stops - %s:%s" % ("", port))
