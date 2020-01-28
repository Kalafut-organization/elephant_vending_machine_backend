# elephants_cse5911
CSE 5911 Capstone Project: Elephant Vending Machine in coordination with Cincinnati Zoo

## Setting up your virtual environment
1. Navigate to the root directory of this project
1. Run `python 3 -m venv .venv` to create a virtual environment
1. Activate your virtual environment
..* On Windows run `.venv\Scripts\activate.bat`
..* On Unix or MacOS run `source .venv/bin/activate`

## Starting the application
1. `export FLASK_APP=elephant_vending_machine`
..* If outside the project directory be sure to include the full path to the application directory
..* OPTIONAL: To enable development features run `export FLASK_ENV=development`
1. `pip install -e .`
1. `flask run`

## Running test suite
To execute the test suite simply run `pytest -v`