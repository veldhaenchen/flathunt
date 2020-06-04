import pytest
import tempfile
import yaml

from flathunter.web import app
from flathunter.web_hunter import WebHunter
from flathunter.idmaintainer import IdMaintainer
from flathunter.config import Config

from dummy_crawler import DummyCrawler

DUMMY_CONFIG = """
urls:
  - https://www.example.com/liste/berlin/wohnungen/mieten?roomi=2&prima=1500&wflmi=70&sort=createdate%2Bdesc
    """

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with tempfile.NamedTemporaryFile(mode='w+') as temp_db:
        config = Config(string=DUMMY_CONFIG)
        config.set_searchers([DummyCrawler()])
        app.config['HUNTER'] = WebHunter(config, IdMaintainer(temp_db.name))

        with app.test_client() as client:
            yield client


def test_get_index(client):
    rv = client.get('/')
    assert b'<h1>Flathunter</h1>' in rv.data

def test_get_index_with_exposes(client):
    app.config['HUNTER'].hunt_flats()
    rv = client.get('/')
    assert b'<div class="expose">' in rv.data