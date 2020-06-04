import logging
import requests
import re
import urllib.request
import urllib.parse
import urllib.error
import datetime
import time
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

    def hunt_flats(self, connection=None):
        new_exposes = []
        processed = self.id_watch.get(connection)

        for url in self.config.get('urls', list()):
            self.__log__.debug('Processing URL: ' + url)
            results = None

            try:
                for searcher in self.config.searchers():
                    if re.search(searcher.URL_PATTERN, url):
                        results = searcher.get_results(url)
                        break
            except requests.exceptions.ConnectionError:
                self.__log__.warning("Connection to %s failed. Retrying. " % url.split('/')[2])
                continue

            # on error, stop execution
            if not results:
                self.__log__.debug('No results for: ' + url)
                continue

            filter = Filter.builder() \
                           .read_config(self.config) \
                           .predicate_filter(lambda e: e['id'] not in processed) \
                           .build()

            processor_chain = ProcessorChain.builder(self.config) \
                                            .apply_filter(filter) \
                                            .map(lambda e: self.__log__.info('New offer: ' + e['title'])) \
                                            .resolve_addresses() \
                                            .calculate_durations() \
                                            .send_telegram_messages() \
                                            .map(lambda e: self.id_watch.add(e['id'], connection)) \
                                            .build()

            new_exposes = new_exposes + list(processor_chain.process(results))

        self.__log__.info(str(len(new_exposes)) + ' new offers found')
        self.id_watch.update_last_run_time(connection)
        return new_exposes

    def get_last_run_time(self, connection=None):
        return self.id_watch.get_last_run_time(connection)