# elephants_cse5911
CSE 5911 Capstone Project: Elephant Vending Machine in coordination with Cincinnati Zoo

![Python package](https://github.com/mknox1225/elephants_cse5911/workflows/Python%20package/badge.svg?branch=master)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

## Setting up your virtual environment
1. Navigate to the root directory of this project
1. Run `python3 -m venv .venv` to create a virtual environment
1. Activate your virtual environment
    * On Windows run `.venv\Scripts\activate.bat`
    * On Unix or MacOS run `source .venv/bin/activate`
    * To deactivate run `deactivate`
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
1. Install coverage.py with `pip install coverage`
1. Install pytest with `pip install pytest`
1. To execute the test suite run `coverage run -m pytest`
1. To view coverage report after tests have been run use `coverage report`

## Linting
1. Install pylint with `pip install pylint`
1. Navigate to the root directory of this project
1. To check your code style, run `pylint elephant_vending_machine`


TEST TEXT PLEASE IGNORE
