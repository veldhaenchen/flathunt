import logging
import re
from random import seed
from random import random
from random import randint
from random import choice

class DummyCrawler:
    __log__ = logging.getLogger(__name__)
    URL_PATTERN = re.compile(r'https://www\.example\.com')

    def __init__(self, titlewords=[ "wg", "tausch", "flat", "ruhig", "gruen" ]):
        seed(1)
        self.titlewords = titlewords

    def get_results(self, search_url):
        self.__log__.debug("Generating dummy results")
        entries = []
        for _ in range(randint(20, 40)):
            expose_id = randint(1, 2000)
            details = {
                'id': expose_id,
                'url': "https://www.example.com/expose/" + str(expose_id),
                'title': "Great flat %s terrible landlord" % (choice(self.titlewords)),
                'price': "%d EUR" % (randint(300, 3000)),
                'size': "%d m^2" % (randint(15, 150)),
                'rooms': "%d" % (randint(1, 5)),
                'address': "1600 Pennsylvania Ave"

            }
            entries.append(details)
        return entries
