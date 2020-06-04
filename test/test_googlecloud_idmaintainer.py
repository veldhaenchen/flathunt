import pytest
import datetime
from mockfirestore import MockFirestore

from flathunter.googlecloud_idmaintainer import GoogleCloudIdMaintainer
from flathunter.config import Config
from flathunter.hunter import Hunter
from dummy_crawler import DummyCrawler
from test_util import count

class MockGoogleCloudIdMaintainer(GoogleCloudIdMaintainer):

    def __init__(self):
        self.db = MockFirestore()

CONFIG_WITH_FILTERS = """
urls:
  - https://www.example.com/liste/berlin/wohnungen/mieten?roomi=2&prima=1500&wflmi=70&sort=createdate%2Bdesc

filters:
  max_price: 1000
    """

@pytest.fixture
def id_watch():
    return MockGoogleCloudIdMaintainer()
    
def test_read_from_empty_db(id_watch):
    assert id_watch.get() == []

def test_read_after_write(id_watch):
    id_watch.mark_processed(12345)
    assert id_watch.get() == [12345]

def test_get_last_run_time_none_by_default(id_watch):
    assert id_watch.get_last_run_time() == None

def test_get_list_run_time_is_updated(id_watch):
    time = id_watch.update_last_run_time()
    assert time != None
    assert time == id_watch.get_last_run_time()

def test_exposes_are_saved_to_maintainer(id_watch):
    config = Config(string=CONFIG_WITH_FILTERS)
    config.set_searchers([DummyCrawler()])
    hunter = Hunter(config, id_watch)
    exposes = hunter.hunt_flats()
    assert count(exposes) > 4
    saved = id_watch.get_exposes_since(datetime.datetime.now() - datetime.timedelta(seconds=10))
    assert len(saved) > 0
    assert count(exposes) < len(saved)

def test_exposes_are_returned_as_dictionaries(id_watch):
    config = Config(string=CONFIG_WITH_FILTERS)
    config.set_searchers([DummyCrawler()])
    hunter = Hunter(config, id_watch)
    hunter.hunt_flats()
    saved = id_watch.get_exposes_since(datetime.datetime.now() - datetime.timedelta(seconds=10))
    assert len(saved) > 0
    expose = saved[0]
    assert expose['title'] is not None

def test_exposes_are_returned_with_limit(id_watch):
    config = Config(string=CONFIG_WITH_FILTERS)
    config.set_searchers([DummyCrawler()])
    hunter = Hunter(config, id_watch)
    hunter.hunt_flats()
    saved = id_watch.get_recent_exposes(10)
    assert len(saved) == 10
    expose = saved[0]
    assert expose['title'] is not None