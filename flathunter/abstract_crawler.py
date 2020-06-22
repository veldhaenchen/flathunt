"""Interface for webcrawlers. Crawler implementations should subclass this"""
import re
import logging
import requests

class Crawler:
    """Defines the Crawler interface"""

    __log__ = logging.getLogger(__name__)
    URL_PATTERN = None

    def get_results(self, search_url, max_pages=None):
        """Loads the exposes from the site, starting at the provided URL"""
        self.__log__.debug("Got search URL %s", search_url)

        # load first page
        soup = self.get_page(search_url)

        # get data from first page
        entries = self.extract_data(soup)
        self.__log__.debug('Number of found entries: %d', len(entries))

        return entries

    def crawl(self, url, max_pages=None):
        """Load as many exposes as possible from the provided URL"""
        if re.search(self.URL_PATTERN, url):
            try:
                return self.get_results(url, max_pages)
            except requests.exceptions.ConnectionError:
                self.__log__.warning("Connection to %s failed. Retrying.", url.split('/')[2])
                return []
        return []

    def get_name(self):
        """Returns the name of this crawler"""
        return type(self).__name__

    def get_expose_details(self, expose):
        """Loads additional detalis for an expose. Should be implemented in the subclass"""
        return expose
