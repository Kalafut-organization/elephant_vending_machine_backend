"""Create Flask application object.

This module creates the Flask appliaction object so that each
module can import it safely and the __name__ variable will always
resolve to the correct package.
"""
from flask import Flask

APP = Flask(__name__)
APP.config.update(
    REMOTE_HOSTS = ['192.168.1.11', '192.168.1.12', '192.168.1.13'],
    REMOTE_HOST_USERNAME = 'pi',
    REMOTE_IMAGE_DIRECTORY = '~/elephant_vending_machine/images'
)

# Circular imports are bad, but views are not used here, only imported, so it's OK
# pylint: disable=wrong-import-position
import elephant_vending_machine.views
