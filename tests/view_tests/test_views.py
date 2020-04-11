import pytest
import os
import subprocess
from flask import jsonify, make_response
import json

from elephant_vending_machine import elephant_vending_machine

class MockLogger:

    @staticmethod
    def info(*args, **kwargs):
        return 

@pytest.fixture
def client():
    elephant_vending_machine.APP.config['TESTING'] = True

    with elephant_vending_machine.APP.test_client() as client:
        yield client

def test_run_trial_route_success(client, monkeypatch):
    monkeypatch.setattr('elephant_vending_machine.views.create_experiment_logger', lambda file_name: MockLogger())
    monkeypatch.setattr('elephant_vending_machine.views.VendingMachine', lambda addresses, config: MockLogger())
    experiment_path = "elephant_vending_machine/static/experiment/unittestExperiment.py"
    subprocess.call(["touch", experiment_path])
    experiment_file = open(experiment_path, 'w')
    experiment_file.write('def run_experiment(experiment_logger, vending_machine):')
    experiment_file.write('    experiment_logger.info("Entered unit test experiment")')
    experiment_file.close()
    response = client.post('/run-experiment?name=unittestExperiment')
    subprocess.call(["rm", "elephant_vending_machine/static/experiment/unittestExperiment.py"])
    assert b'Running unittestExperiment' in response.data
    assert response.status_code == 200

def test_run_trial_route_empty_query_string(client):
    response = client.post('/run-experiment')
    assert b'No experiment_name specified' in response.data
    assert response.status_code == 400
