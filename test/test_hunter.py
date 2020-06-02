import unittest
import yaml
import re
from flathunter.crawl_immowelt import CrawlImmowelt
from flathunter.hunter import Hunter 
from flathunter.config import Config
from flathunter.idmaintainer import IdMaintainer
from dummy_crawler import DummyCrawler

class HunterTest(unittest.TestCase):

    DUMMY_CONFIG = """
urls:
  - https://www.immowelt.de/liste/berlin/wohnungen/mieten?roomi=2&prima=1500&wflmi=70&sort=createdate%2Bdesc

google_maps_api:
  key: SOME_KEY
  url: https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={dest}&mode={mode}&sensor=true&key={key}&arrival_time={arrival}
  enable: true
    """

    FILTER_TITLES_CONFIG = """
urls:
  - https://www.example.com/search/flats-in-berlin

filters:
  excluded_titles:
    - "wg"
    - "tausch"
    - "wochenendheimfahrer"
    - "pendler"
    - "zwischenmiete"
"""

    FILTER_MIN_PRICE_CONFIG = """
urls:
  - https://www.example.com/search/flats-in-berlin

filters:
  min_price: 700
"""

    FILTER_MAX_PRICE_CONFIG = """
urls:
  - https://www.example.com/search/flats-in-berlin

filters:
  max_price: 1000
"""

    FILTER_MIN_SIZE_CONFIG = """
urls:
  - https://www.example.com/search/flats-in-berlin

filters:
  min_size: 80
"""

    FILTER_MAX_SIZE_CONFIG = """
urls:
  - https://www.example.com/search/flats-in-berlin

filters:
  max_size: 80
"""

    FILTER_TITLES_LEGACY_CONFIG = """
urls:
  - https://www.example.com/search/flats-in-berlin

excluded_titles:
  - "wg"
  - "tausch"
  - "wochenendheimfahrer"
  - "pendler"
  - "zwischenmiete"
"""

    def test_hunt_flats(self):
        hunter = Hunter(Config(string=self.DUMMY_CONFIG), [CrawlImmowelt()], IdMaintainer(":memory:"))
        exposes = hunter.hunt_flats()
        self.assertTrue(len(exposes) > 0, "Expected to find exposes")

    def test_invalid_config(self):
        with self.assertRaises(Exception) as context:
            Hunter(dict(), [CrawlImmowelt()], IdMaintainer(":memory:"))

        self.assertTrue('Invalid config' in str(context.exception))

    def test_filter_titles_legacy(self):
        titlewords = [ "wg", "tausch", "flat", "ruhig", "gruen" ]
        filteredwords = [ "wg", "tausch", "wochenendheimfahrer", "pendler", "zwischenmiete" ]
        hunter = Hunter(Config(string=self.FILTER_TITLES_LEGACY_CONFIG), [DummyCrawler(titlewords)], IdMaintainer(":memory:"))
        exposes = hunter.hunt_flats()
        self.assertTrue(len(exposes) > 4, "Expected to find exposes")
        unfiltered = list(filter(lambda expose: any(word in expose['title'] for word in filteredwords), exposes))
        if len(unfiltered) > 0:
            for expose in unfiltered:
                print("Got expose: ", expose)
        self.assertTrue(len(unfiltered) == 0, "Expected words to be filtered")

    def test_filter_titles(self):
        titlewords = [ "wg", "tausch", "flat", "ruhig", "gruen" ]
        filteredwords = [ "wg", "tausch", "wochenendheimfahrer", "pendler", "zwischenmiete" ]
        hunter = Hunter(Config(string=self.FILTER_TITLES_CONFIG), [DummyCrawler(titlewords)], IdMaintainer(":memory:"))
        exposes = hunter.hunt_flats()
        self.assertTrue(len(exposes) > 4, "Expected to find exposes")
        unfiltered = list(filter(lambda expose: any(word in expose['title'] for word in filteredwords), exposes))
        if len(unfiltered) > 0:
            for expose in unfiltered:
                print("Got unfiltered expose: ", expose)
        self.assertTrue(len(unfiltered) == 0, "Expected words to be filtered")

    def test_filter_min_price(self):
        min_price = 700
        hunter = Hunter(Config(string=self.FILTER_MIN_PRICE_CONFIG), [DummyCrawler()], IdMaintainer(":memory:"))
        exposes = hunter.hunt_flats()
        self.assertTrue(len(exposes) > 4, "Expected to find exposes")
        unfiltered = list(filter(lambda expose: float(re.search(r'\d+([\.,]\d+)?', expose['price'])[0]) < min_price, exposes))
        if len(unfiltered) > 0:
            for expose in unfiltered:
                print("Got unfiltered expose: ", expose)
        self.assertTrue(len(unfiltered) == 0, "Expected cheap flats to be filtered")

    def test_filter_max_price(self):
        max_price = 1000
        hunter = Hunter(Config(string=self.FILTER_MAX_PRICE_CONFIG), [DummyCrawler()], IdMaintainer(":memory:"))
        exposes = hunter.hunt_flats()
        self.assertTrue(len(exposes) > 4, "Expected to find exposes")
        unfiltered = list(filter(lambda expose: float(re.search(r'\d+([\.,]\d+)?', expose['price'])[0]) > max_price, exposes))
        if len(unfiltered) > 0:
            for expose in unfiltered:
                print("Got unfiltered expose: ", expose)
        self.assertTrue(len(unfiltered) == 0, "Expected expensive flats to be filtered")

    def test_filter_max_size(self):
        max_size = 80
        hunter = Hunter(Config(string=self.FILTER_MAX_SIZE_CONFIG), [DummyCrawler()], IdMaintainer(":memory:"))
        exposes = hunter.hunt_flats()
        self.assertTrue(len(exposes) > 4, "Expected to find exposes")
        unfiltered = list(filter(lambda expose: float(re.search(r'\d+([\.,]\d+)?', expose['size'])[0]) > max_size, exposes))
        if len(unfiltered) > 0:
            for expose in unfiltered:
                print("Got unfiltered expose: ", expose)
        self.assertTrue(len(unfiltered) == 0, "Expected big flats to be filtered")

    def test_filter_min_size(self):
        min_size = 80
        hunter = Hunter(Config(string=self.FILTER_MIN_SIZE_CONFIG), [DummyCrawler()], IdMaintainer(":memory:"))
        exposes = hunter.hunt_flats()
        self.assertTrue(len(exposes) > 4, "Expected to find exposes")
        unfiltered = list(filter(lambda expose: float(re.search(r'\d+([\.,]\d+)?', expose['size'])[0]) < min_size, exposes))
        if len(unfiltered) > 0:
            for expose in unfiltered:
                print("Got unfiltered expose: ", expose)
        self.assertTrue(len(unfiltered) == 0, "Expected small flats to be filtered")
