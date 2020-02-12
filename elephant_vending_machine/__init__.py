"""Create Flask application object.

This module creates the Flask appliaction object so that each
module can import it safely and the __name__ variable will always
resolve to the correct package.
"""
import os
from flask import Flask

IMAGE_UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/static/img'

APP = Flask(__name__)
APP.config['IMAGE_UPLOAD_FOLDER'] = IMAGE_UPLOAD_FOLDER

# Circular imports are bad, but views are not used here, only imported, so it's OK
# pylint: disable=wrong-import-position
import elephant_vending_machine.views
