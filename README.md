# Elephant Vending Machine
OSU CSE 5911 Capstone Project: Elephant Vending Machine in coordination with Cincinnati Zoo. Designed to facilitate automated behavioral psychology experiments.

![Python package](https://github.com/mknox1225/elephants_cse5911/workflows/Python%20package/badge.svg?branch=master)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/Kalafut-organization/elephants_cse5911/blob/master/LICENSE.md)
[![codecov](https://codecov.io/gh/Kalafut-organization/elephants_cse5911/branch/master/graph/badge.svg)](https://codecov.io/gh/Kalafut-organization/elephants_cse5911)
[![Documentation Status](https://readthedocs.org/projects/elephants-cse5911/badge/?version=latest)](https://elephants-cse5911.readthedocs.io/en/latest/?badge=latest)


## Setting up your virtual environment and installing dependencies
1. Navigate to the root directory of this project
1. Run `python3 -m venv .venv` to create a virtual environment
1. Activate your virtual environment
    * On Windows run `.venv\Scripts\activate.bat`
    * On Unix or MacOS run `source .venv/bin/activate`
    * To deactivate run `deactivate`
    * NOTE: You will need to activate your virtual environment every time you close and reopen your terminal
1. Use `pip install -r requirements.txt` to install all required dependencies

## Starting the application
1. Tell Flask where to find application instance
    * On Windows run `set FLASK_APP=elephant_vending_machine`
    * On Unix or MacOS run `export FLASK_APP=elephant_vending_machine`
    * If outside the project directory be sure to include the full path to the application directory
    * OPTIONAL: To enable development features run `export FLASK_ENV=development` on Unix or `set FLASK_ENV=development` on Windows
1. `pip install -e .`
1. `flask run`

## Configuring Remote Pis for GPIO Pin Reading
1. Ensure Pis are running Raspbian
1. Open the Raspberry Pi Configuration Tool
1. Set "Remote GPIO" to "enabled"
1. Configure this to run at boot in the future
    * Using a terminal, run the following `sudo systemctl enable pigpiod`
    * Now to manually enable remote access at this time, run `sudo systemctl start pigpiod`
1. For more information, visit [this documentation](https://gpiozero.readthedocs.io/en/stable/remote_gpio.html)

## Configuring Remote Pis for RGB LED Strip Interfacing
1. Follow this reference: https://tutorials-raspberrypi.com/connect-control-raspberry-pi-ws2812-rgb-led-strips/
1. For our purposes, we did not use an external power source and found the power provided by the pi to be sufficient.

## Dependencies for Image Display
1. Image display is done by utilizing feh: https://linux.die.net/man/1/feh
1. To install feh, run `sudo apt install feh` while connected via SSH to the pi.
* Note, this will need to be done on each of the remote pis only, the web server does not require installion of feh.

## Test suite
1. To execute the test suite run `coverage run -m pytest`
1. To view coverage report after tests have been run use `coverage report`

## Linting
1. Navigate to the root directory of this project
1. To check your code style, run `pylint elephant_vending_machine`

## Build and view API documentation
1. Navigate to `docs` directory
1. `make html` to build API documentation
1. Open `index.html` under `docs/_build/html/` in a browser to view documentation
    * The master branch documentation can be viewed on Read the Docs by clicking the "docs" badge at the top of this README

## Running on Raspberry Pi
1. Connect to your Raspberry Pi
1. Clone this repo to the Pi
1. Navigate to the cloned directory
1. Run `pip install gunicorn3`
1. Run `gunicorn3 -b 0.0.0.0:8080 elephant_vending_machine:APP`
