import unittest
import datetime
import re

from flathunter.idmaintainer import IdMaintainer
from flathunter.config import Config
from flathunter.hunter import Hunter
from flathunter.filter import Filter
from dummy_crawler import DummyCrawler
from test_util import count

class IdMaintainerTest(unittest.TestCase):

    TEST_URL = 'https://www.immowelt.de/liste/berlin/wohnungen/mieten?roomi=2&prima=1500&wflmi=70&sort=createdate%2Bdesc'

    DUMMY_CONFIG = """
urls:
  - https://www.example.com/liste/berlin/wohnungen/mieten?roomi=2&prima=1500&wflmi=70&sort=createdate%2Bdesc
    """

    CONFIG_WITH_FILTERS = """
urls:
  - https://www.example.com/liste/berlin/wohnungen/mieten?roomi=2&prima=1500&wflmi=70&sort=createdate%2Bdesc

filters:
  max_price: 1000
    """

    def setUp(self):
        self.maintainer = IdMaintainer(":memory:")

    def test_read_from_empty_db(self):
        self.assertEqual(0, len(self.maintainer.get()), "Expected empty db to return empty array")

    def test_read_after_write(self):
        self.maintainer.mark_processed(12345)
        self.assertEqual(12345, self.maintainer.get()[0], "Expected ID to be saved")

    def test_get_last_run_time_none_by_default(self):
        self.assertIsNone(self.maintainer.get_last_run_time(), "Expected last run time to be none")

    def test_get_list_run_time_is_updated(self):
        time = self.maintainer.update_last_run_time()
        self.assertIsNotNone(time, "Expected time not to be none")
        self.assertEqual(time, self.maintainer.get_last_run_time(), "Expected last run time to be updated")

def test_ids_are_added_to_maintainer(mocker):
    config = Config(string=IdMaintainerTest.DUMMY_CONFIG)
    config.set_searchers([DummyCrawler()])
    id_watch = IdMaintainer(":memory:")
    spy = mocker.spy(id_watch, "mark_processed")
    hunter = Hunter(config, id_watch)
    exposes = hunter.hunt_flats()
    assert count(exposes) > 4
    assert spy.call_count == 24

def test_exposes_are_saved_to_maintainer():
    config = Config(string=IdMaintainerTest.CONFIG_WITH_FILTERS)
    config.set_searchers([DummyCrawler()])
    id_watch = IdMaintainer(":memory:")
    hunter = Hunter(config, id_watch)
    exposes = hunter.hunt_flats()
    assert count(exposes) > 4
    saved = id_watch.get_exposes_since(datetime.datetime.now() - datetime.timedelta(seconds=10))
    assert len(saved) > 0
    assert count(exposes) < len(saved)

def test_exposes_are_returned_as_dictionaries():
    config = Config(string=IdMaintainerTest.CONFIG_WITH_FILTERS)
    config.set_searchers([DummyCrawler()])
    id_watch = IdMaintainer(":memory:")
    hunter = Hunter(config, id_watch)
    hunter.hunt_flats()
    saved = id_watch.get_exposes_since(datetime.datetime.now() - datetime.timedelta(seconds=10))
    assert len(saved) > 0
    expose = saved[0]
    assert expose['title'] is not None

def test_exposes_are_returned_with_limit():
    config = Config(string=IdMaintainerTest.CONFIG_WITH_FILTERS)
    config.set_searchers([DummyCrawler()])
    id_watch = IdMaintainer(":memory:")
    hunter = Hunter(config, id_watch)
    hunter.hunt_flats()
    saved = id_watch.get_recent_exposes(10)
    assert len(saved) == 10
    expose = saved[0]
    assert expose['title'] is not None

def test_exposes_are_returned_filtered():
    config = Config(string=IdMaintainerTest.CONFIG_WITH_FILTERS)
    config.set_searchers([DummyCrawler()])
    id_watch = IdMaintainer(":memory:")
    hunter = Hunter(config, id_watch)
    hunter.hunt_flats()
    filter = Filter.builder().max_size_filter(70).build()
    saved = id_watch.get_recent_exposes(10, filter=filter)
    for expose in saved:
        assert int(re.match(r'\d+', expose['size'])[0]) <= 70

def test_filters_for_user_are_saved():
    id_watch = IdMaintainer(":memory:")
    filter = { 'fish': 'cat' }
    id_watch.set_filters_for_user(123, filter)
    assert id_watch.get_filters_for_user(123) == filter

def test_all_filters_can_be_loaded():
    id_watch = IdMaintainer(":memory:")
    filter = { 'fish': 'cat' }
    id_watch.set_filters_for_user(123, filter)
    id_watch.set_filters_for_user(124, filter)
    assert id_watch.get_user_filters() == [ (123, filter), (124, filter) ]
