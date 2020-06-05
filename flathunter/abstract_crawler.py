import requests
import re
import logging

class Crawler:

    __log__ = logging.getLogger(__name__)

    def crawl(self, url, max_pages=None):
        if re.search(self.URL_PATTERN, url):
            try:
                return self.get_results(url, max_pages)
            except requests.exceptions.ConnectionError:
                self.__log__.warning("Connection to %s failed. Retrying. " % url.split('/')[2])
                return []
        return []

    def get_name(self):
        return type(self).__name__