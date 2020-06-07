import logging
import requests
import re
from itertools import chain

from flathunter.config import Config
from flathunter.filter import Filter
from flathunter.processor import ProcessorChain

class Hunter:
    __log__ = logging.getLogger(__name__)

    def __init__(self, config, id_watch):
        self.config = config
        if not isinstance(self.config, Config):
            raise Exception("Invalid config for hunter - should be a 'Config' object")
        self.id_watch = id_watch

    def crawl_for_exposes(self, max_pages=None):
        return chain(*[ searcher.crawl(url, max_pages)
                        for searcher in self.config.searchers()
                        for url in self.config.get('urls', list()) ])

    def hunt_flats(self, max_pages=None):
        filter = Filter.builder() \
                       .read_config(self.config) \
                       .filter_already_seen(self.id_watch) \
                       .build()

        processor_chain = ProcessorChain.builder(self.config) \
                                        .save_all_exposes(self.id_watch) \
                                        .apply_filter(filter) \
                                        .resolve_addresses() \
                                        .calculate_durations() \
                                        .send_telegram_messages() \
                                        .build()

        result = []
        # We need to iterate over this list to force the evaluation of the pipeline
        for expose in processor_chain.process(self.crawl_for_exposes(max_pages)):
            self.__log__.info('New offer: ' + expose['title'])
            result.append(expose)

        return result