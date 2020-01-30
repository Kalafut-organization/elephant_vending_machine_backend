import pytest

from elephant_vending_machine import elephant_vending_machine


@pytest.fixture
def client():
    elephant_vending_machine.APP.config['TESTING'] = True

    with elephant_vending_machine.APP.test_client() as client:
        yield client

def test_root_route(client):
    response = client.get('/')
    assert b'Hello Elephantsa!' in response.data
