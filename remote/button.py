from gpiozero import Button
import requests
import time
import subprocess

class Sensor:
    def __init__(self, sensor_pin):
        self.sensor_pin = sensor_pin
        self.button = Button(sensor_pin)
    
    def read(self):
        """Returns true if sensor is active"""
        return self.button.is_active

pins = [2,3,4,14,15,18]

sensors = []
for pin in pins:
    sensors.append(Sensor(pin))

while True:
    readings = [False] * len(sensors)
    while not any(readings):
        readings = [sensor.read() for sensor in sensors]
    url = "http://192.168.0.100/signal"
    p = subprocess.Popen(['hostname', '-I'], stdout=subprocess.PIPE)
    out = p.communicate()
    data = {"address": out[0].strip()}

    requests.post(url, data = data)
    time.sleep(0.5)