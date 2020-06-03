import pytest
import tempfile
import yaml

from flathunter.web import app
from flathunter.hunter import Hunter
from flathunter.idmaintainer import IdMaintainer
from flathunter.crawl_immowelt import CrawlImmowelt
from flathunter.config import Config

DUMMY_CONFIG = """
urls:
  - https://www.immowelt.de/liste/berlin/wohnungen/mieten?roomi=2&prima=1500&wflmi=70&sort=createdate%2Bdesc
    """

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with tempfile.NamedTemporaryFile(mode='w+') as temp_db:
        config = Config(string=DUMMY_CONFIG)
        config.set_searchers([CrawlImmowelt()])
        app.config['HUNTER'] = Hunter(config, IdMaintainer(temp_db.name))

        with app.test_client() as client:
            yield client


def test_get_index(client):
    rv = client.get('/')
    assert b'<h1>Flathunter</h1>' in rv.data
