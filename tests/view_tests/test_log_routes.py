import pytest
import subprocess
from io import BytesIO
import json

from elephant_vending_machine import elephant_vending_machine
from subprocess import CompletedProcess, CalledProcessError

def raise_(ex):
    raise ex

@pytest.fixture
def client():
    elephant_vending_machine.APP.config['TESTING'] = True

    with elephant_vending_machine.APP.test_client() as client:
        yield client
        subprocess.call(["rm","elephant_vending_machine/static/log/test_file.csv"])
        subprocess.call(["rm","elephant_vending_machine/static/log/test_file2.csv"])
        subprocess.call(["rm", "elephant_vending_machine/static/log/empty.csv"])

def test_get_log_endpoint(client):
    subprocess.call(["touch", "elephant_vending_machine/static/log/test_file.csv"])
    subprocess.call(["touch", "elephant_vending_machine/static/log/test_file2.csv"])
    response = client.get('/log')
    response_json_files = json.loads(response.data)['files']
    min_elements_expected = ["http://localhost/static/log/test_file.csv","http://localhost/static/log/test_file2.csv","http://localhost/static/log/unittest.csv"]
    assert all(elem in response_json_files for elem in min_elements_expected)
    assert response.status_code == 200

def test_delete_log_happy_path(client):
    subprocess.call(["touch", "elephant_vending_machine/static/log/empty.csv"])
    response = client.delete('/log/empty.csv')
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'File empty.csv was successfully deleted.'

def test_delete_log_file_not_found(client):
    response = client.delete('/log/empty.csv')
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'File empty.csv does not exist and so couldn\'t be deleted.'

def test_delete_log_is_a_directory_exception(client, monkeypatch):
    subprocess.call(["touch", "elephant_vending_machine/static/log/empty.csv"])
    monkeypatch.setattr('os.remove', lambda file: (_ for _ in ()).throw(IsADirectoryError))
    response = client.delete('/log/empty.csv')
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'empty.csv exists, but is a directory and not a file. Deletion failed.'