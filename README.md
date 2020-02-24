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
