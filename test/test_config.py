import unittest
import tempfile
import os.path
import os
from flathunter.config import Config 

class ConfigTest(unittest.TestCase):

    DUMMY_CONFIG = """
urls:
  - https://www.immowelt.de/liste/berlin/wohnungen/mieten?roomi=2&prima=1500&wflmi=70&sort=createdate%2Bdesc
    """

    def test_loads_config(self):
        created = False
        if not os.path.isfile("config.yaml"):
            config_file = open("config.yaml", "w")
            config_file.write(self.DUMMY_CONFIG)
            config_file.flush()
            config_file.close()
            created = True
        config = Config()
        self.assertTrue(len(config.get('urls')) > 0, "Expected URLs in config file")
        if created:
            os.remove("config.yaml")

    def test_loads_config_at_file(self):
       with tempfile.NamedTemporaryFile(mode='w+') as temp:
          temp.write(self.DUMMY_CONFIG)
          temp.flush()
          config = Config(temp.name) 
       self.assertTrue(len(config.get('urls')) > 0, "Expected URLs in config file")
