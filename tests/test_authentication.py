import json
import pytest

from src import application
from src.configuration import Manifest


@pytest.fixture
def client():
    application.config['TESTING'] = True
    client = application.test_client()
    yield client


def test_authentication_validation():
    with open('addon-manifest.json') as f:
        data = json.load(f)
    manifest = Manifest.decode(data)
    # import pdb; pdb.set_trace()
    header = 'Basic YWRkb24tc2x1ZzpzdXBlci1zZWNyZXQ='
    assert not manifest.validate(header.split()[-1])


# def test_authentication(client):
#     response = client.post('/heroku/resources', headers={
#         'Authorization': 'Basic YWRkb24tc2x1ZzpzdXBlci1zZWNyZXQ=',
#     })
#     assert response.status_code == 401
