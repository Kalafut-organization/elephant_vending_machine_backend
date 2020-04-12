import pytest
import os
import subprocess
from flask import jsonify, make_response
import json

from elephant_vending_machine import elephant_vending_machine

class MockLogger:

    def info(self, *args, **kwargs):
        self.args = list(args)
 

@pytest.fixture
def client():
    elephant_vending_machine.APP.config['TESTING'] = True

    with elephant_vending_machine.APP.test_client() as client:
        yield client

def test_run_trial_route_success(client, monkeypatch):
    mock_logger = MockLogger()
    monkeypatch.setattr('elephant_vending_machine.views.create_experiment_logger', lambda file_name: mock_logger)

    experiment_path = "elephant_vending_machine/static/experiment/unittestExperiment.py"
    subprocess.call(["touch", experiment_path])
    experiment_file = open(experiment_path, 'w')
    experiment_file.write('def run_experiment(experiment_logger, vending_machine):')
    experiment_file.write('    experiment_logger.info("Entered unit test experiment")')
    experiment_file.close()

    response = client.post('/run-experiment/unittestExperiment.py')
    assert b'Running unittestExperiment' in response.data
    assert response.status_code == 200
    assert mock_logger.args == ['Entered unit test experiment']
    subprocess.call(["rm", "elephant_vending_machine/static/experiment/unittestExperiment.py"])

def test_run_trial_experiment_file_doesnt_exist(client):
    response = client.post('/run-experiment/aNonexistentExperiment.py')
    assert b'No experiment named aNonexistentExperiment' in response.data
    assert response.status_code == 400
