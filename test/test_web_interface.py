import pytest

from flathunter.web import app

@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_get_index(client):
    rv = client.get('/')
    assert b'<h1>Flathunter</h1>' in rv.data
