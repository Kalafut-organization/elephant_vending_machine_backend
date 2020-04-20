# Elephant Vending Machine
OSU CSE 5911 Capstone Project: Elephant Vending Machine in coordination with Cincinnati Zoo. Designed to facilitate automated behavioral psychology experiments.

[![build](https://github.com/Kalafut-organization/elephant_vending_machine_backend/workflows/build/badge.svg)](https://github.com/Kalafut-organization/elephant_vending_machine_backend/actions?query=workflow%3Abuild)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/Kalafut-organization/elephants_cse5911/blob/master/LICENSE.md)
[![codecov](https://codecov.io/gh/Kalafut-organization/elephant_vending_machine_backend/branch/master/graph/badge.svg)](https://codecov.io/gh/Kalafut-organization/elephant_vending_machine_backend)
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
NOTE: See section "Running in Production" if you intend to make calls from the front-end
1. Tell Flask where to find application instance
    * On Windows run `set FLASK_APP=elephant_vending_machine`
    * On Unix or MacOS run `export FLASK_APP=elephant_vending_machine`
    * If outside the project directory be sure to include the full path to the application directory
    * OPTIONAL: To enable development features run `export FLASK_ENV=development` on Unix or `set FLASK_ENV=development` on Windows
1. `pip install -e .`
1. `flask run`

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

## Running in production
NOTE: This step is necessary to allow the front-end to make API calls. If you don't run the project using Docker it uses a port that the front-end is not expecting and API calls will fail. If running on a device without the sonar sensors connected (such as your dev machine),
you'll have to remove the `devices` line from the `docker-compose.yml` file. You'll also need to add a file called `id_rsa` to the project
folder. If using the image syncing, this must be a passwordless SSH key that has been set up with the remote machines to sync images to. Otherwise, it can be an empty file.

1. Connect to your Raspberry Pi
1. Clone this repo to the Pi
1. Navigate to the cloned directory
1. [Install docker and docker-compose](https://dev.to/rohansawant/installing-docker-and-docker-compose-on-the-raspberry-pi-in-5-simple-steps-3mgl)
1. Run `docker-compose up --build` to start the containers
    * This will ensure the containers automatically restart in case of error or reboots.
    * To stop the containers, and avoid auto-restarting, use `docker-compose down`
    * Container storage is persisted between runs
