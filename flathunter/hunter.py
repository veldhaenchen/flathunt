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

    def hunt_flats(self):
        filter = Filter.builder() \
                       .read_config(self.config) \
                       .filter_already_seen(self.id_watch) \
                       .build()

        processor_chain = ProcessorChain.builder(self.config) \
                                        .apply_filter(filter) \
                                        .map(lambda e: self.__log__.info('New offer: ' + e['title'])) \
                                        .resolve_addresses() \
                                        .calculate_durations() \
                                        .send_telegram_messages() \
                                        .build()

        new_exposes = chain(*[ processor_chain.process(searcher.crawl(url))
                                for searcher in self.config.searchers()
                                for url in self.config.get('urls', list()) ])

        self.id_watch.update_last_run_time()
        return new_exposes

    def get_last_run_time(self):
        return self.id_watch.get_last_run_time()