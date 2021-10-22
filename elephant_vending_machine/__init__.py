"""Create Flask application object.

This module creates the Flask appliaction object so that each
module can import it safely and the __name__ variable will always
resolve to the correct package.
"""
from flask import Flask
from flask_cors import CORS, cross_origin
import subprocess
import atexit

APP = Flask(__name__)
CORS(APP)
APP.config.update(
    REMOTE_HOSTS=['192.168.0.11', '192.168.0.12', '192.168.0.13'],
    REMOTE_HOST_USERNAME='pi',
    REMOTE_IMAGE_DIRECTORY='/home/pi/elephant_vending_machine/images'
)

for host in APP.config['REMOTE_HOSTS']:
    user = APP.config['REMOTE_HOST_USERNAME']
    subprocess.Popen(['ssh', f'''{user}@{host}''', 'python', '/home/pi/button/button.py'])

def kill_processes():
    for host in APP.config['REMOTE_HOSTS']:
        user = APP.config['REMOTE_HOST_USERNAME']
        subprocess.Popen(['ssh', f'''{user}@{host}''', 'pkill', '-f', 'button.py'])
    print("Test")

atexit.register(kill_processes)

# Circular imports are bad, but views are not used here, only imported, so it's OK
# pylint: disable=wrong-import-position
import elephant_vending_machine.views
