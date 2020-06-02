import unittest
import yaml
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

    def test_filter_titles(self):
        titlewords = [ "wg", "tausch", "flat", "ruhig", "gruen" ]
        filteredwords = [ "wg", "tausch", "wochenendheimfahrer", "pendler", "zwischenmiete" ]
        hunter = Hunter(Config(string=self.FILTER_TITLES_CONFIG), [DummyCrawler(titlewords)], IdMaintainer(":memory:"))
        exposes = hunter.hunt_flats()
        self.assertTrue(len(exposes) > 4, "Expected to find exposes")
        unfiltered = list(filter(lambda expose: any(word in expose['title'] for word in filteredwords), exposes))
        if len(unfiltered) > 0:
            for expose in unfiltered:
                print("Got expose: ", expose)
        self.assertTrue(len(unfiltered) == 0, "Expected words to be filtered")
