import os
import yaml
import logging

class Config:

    __log__ = logging.getLogger(__name__)

    def __init__(self, filename=None, string=None):
        if string is not None:
            self.config = yaml.safe_load(string)
            return
        if filename is None:
            filename = os.path.dirname(os.path.abspath(__file__)) + "/../config.yaml"
        self.__log__.info("Using config %s" % filename)
        with open(filename) as file:
            self.config = yaml.safe_load(file)

    def __iter__(self):
        return self.config.__iter__()

    def get(self, key, value=None):
        return self.config.get(key, value)
