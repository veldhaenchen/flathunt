"""Wrap configuration options as an object"""
import os
import logging
import yaml

from flathunter.captcha.imagetypers_solver import ImageTypersSolver
from flathunter.captcha.twocaptcha_solver import TwoCaptchaSolver
from flathunter.captcha.captcha_solver import CaptchaSolver
from flathunter.crawl_ebaykleinanzeigen import CrawlEbayKleinanzeigen
from flathunter.crawl_immobilienscout import CrawlImmobilienscout
from flathunter.crawl_wggesucht import CrawlWgGesucht
from flathunter.crawl_immowelt import CrawlImmowelt
from flathunter.crawler_subito import CrawlSubito
from flathunter.crawl_immobiliare import CrawlImmobiliare
from flathunter.crawl_idealista import CrawlIdealista
from flathunter.filter import Filter

class Config:
    """Class to represent flathunter configuration"""

    __log__ = logging.getLogger('flathunt')

    def __init__(self, filename=None, string=None):
        if string is not None:
            self.config = yaml.safe_load(string)
        else:
            if filename is None:
                filename = os.path.dirname(os.path.abspath(__file__)) + "/../config.yaml"
            self.__log__.info("Using config %s", filename)
            with open(filename) as file:
                self.config = yaml.safe_load(file)
        self.__searchers__ = [CrawlImmobilienscout(self),
                              CrawlWgGesucht(self),
                              CrawlEbayKleinanzeigen(self),
                              CrawlImmowelt(self),
                              CrawlSubito(self),
                              CrawlImmobiliare(self),
                              CrawlIdealista(self)]

    def __iter__(self):
        """Emulate dictionary"""
        return self.config.__iter__()

    def __getitem__(self, value):
        """Emulate dictionary"""
        return self.config[value]

    def get(self, key, value=None):
        """Emulate dictionary"""
        return self.config.get(key, value)

    def database_location(self):
        """Return the location of the database folder"""
        if "database_location" in self.config:
            return self.config["database_location"]
        return os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/..")

    def set_searchers(self, searchers):
        """Update the active search plugins"""
        self.__searchers__ = searchers

    def searchers(self):
        """Get the list of search plugins"""
        return self.__searchers__

    def get_filter(self):
        """Read the configured filter"""
        builder = Filter.builder()
        builder.read_config(self.config)
        return builder.build()

    def captcha_enabled(self):
        return ("captcha" in self.config)

    def get_captcha_solver(self) -> CaptchaSolver:
        captcha_config = self.config.get("captcha", dict())

        imagetypers_token = captcha_config.get("imagetypers", dict()).get("token", "")
        twocaptcha_api_key = captcha_config.get("2captcha", dict()).get("api_key", "")

        if imagetypers_token:
            return ImageTypersSolver(imagetypers_token)
        elif twocaptcha_api_key:
            return TwoCaptchaSolver(twocaptcha_api_key)
        else:
            raise Exception("No captcha solver configured properly.")


    def use_proxy(self):
        return ("use_proxy_list" in self.config and self.config["use_proxy_list"])
