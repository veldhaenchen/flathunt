import os
import yaml
import logging

from flathunter.filter import Filter

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

    def __getitem__(self, value):
        return self.config[value]

    def get(self, key, value=None):
        return self.config.get(key, value)

    def get_filter(self):
        builder = Filter.builder()
        if "excluded_titles" in self.config:
            builder.title_filter(self.config["excluded_titles"])
        if "filters" in self.config:
            filters_config = self.config["filters"]
            if "excluded_titles" in filters_config:
                builder.title_filter(filters_config["excluded_titles"])
            if "min_price" in filters_config:
                builder.min_price_filter(filters_config["min_price"])
            if "max_price" in filters_config:
                builder.max_price_filter(filters_config["max_price"])
            if "min_size" in filters_config:
                builder.min_size_filter(filters_config["min_size"])
            if "max_size" in filters_config:
                builder.max_size_filter(filters_config["max_size"])
        return builder.build()
