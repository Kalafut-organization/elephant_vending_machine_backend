import pytest
from io import BytesIO

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


def test_post_image_route_no_file(client):
    response = client.post('/image')
    assert response.status_code == 400
    assert b'Error with request: No file field in body of request.' in response.data

def test_post_image_route_empty_filename(client):
    data = {'file': (BytesIO(b"Testing: \x00\x01"), '')}
    response = client.post('/image', data=data) 
    assert response.status_code == 400
    assert b'Error with request: File field in body of response with no file present.' in response.data

def test_post_image_route_with_file_bad_extension(client):
    data = {'file': (BytesIO(b"Testing: \x00\x01"), 'test_file.sh')}
    response = client.post('/image', data=data) 
    assert response.status_code == 400
    assert b'Error with request: File extension not allowed.' in response.data

def test_post_image_route_with_file(client):
    data = {'file': (BytesIO(b"Testing: \x00\x01"), 'test_file.png')}
    response = client.post('/image', data=data) 
    assert response.status_code == 200
    assert b'Success: Image saved.' in response.data