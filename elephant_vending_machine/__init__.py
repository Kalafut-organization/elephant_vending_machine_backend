"""Create Flask application object.

This module creates the Flask appliaction object so that each
module can import it safely and the __name__ variable will always
resolve to the correct package.
"""
from flask import Flask

APP = Flask(__name__)

# Circular imports are bad, but views are not used here, only imported, so it's OK
# pylint: disable=wrong-import-position
import elephant_vending_machine.views
