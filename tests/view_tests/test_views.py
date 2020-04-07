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
        subprocess.call(["rm", "elephant_vending_machine/static/experiment/unittestExperiment.py"])

def test_run_trial_route_success(client, monkeypatch):
    monkeypatch.setattr('elephant_vending_machine.views.create_experiment_logger', lambda file_name: MockLogger())
    monkeypatch.setattr('elephant_vending_machine.views.VendingMachine', lambda addresses, config: MockLogger())
    subprocess.call(["touch", "elephant_vending_machine/static/experiment/unittestExperiment.py"])
    response = client.post('/run-trial?trial_name=unittestExperiment')
    assert b'Running demo' in response.data
    assert response.status_code == 200

def test_run_trial_route_empty_query_string(client):
    response = client.post('/run-trial')
    assert b'No trial_name specified' in response.data
    assert response.status_code == 400
