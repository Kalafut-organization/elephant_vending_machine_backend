import pytest

from elephant_vending_machine import elephant_vending_machine


@pytest.fixture
def client():
    elephant_vending_machine.APP.config['TESTING'] = True

    with elephant_vending_machine.APP.test_client() as client:
        yield client

def test_root_route(client):
    response = client.get('/')
    assert b'Hello Elephants!' in response.data

def test_run_trial_route_sucess(client):
    response = client.get('/run-trial?trial_name=demo')
    assert b'Running demo' in response.data

def test_run_trial_route_empty_query_string(client):
    response = client.get('/run-trial')
    assert b'No trial_name specified' in response.data

def test_add_image_route_no_file(client):
    response = client.post('/add-image')
    assert b'No image file in request' in response.data

def test_get_log_route_success(client):
    response = client.get('/get-log?log_name=alog')
    assert b'This would be alog' in response.data

def test_get_log_route_no_log_name(client):
    response = client.get('/get-log')
    assert b'Error with request.' in response.data
    