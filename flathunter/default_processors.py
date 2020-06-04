import re
import logging
from flathunter.abstract_processor import Processor

class Filter(Processor):
    
    def __init__(self, config, filter):
        self.config = config
        self.filter = filter
    
    def process_exposes(self, exposes):
        return self.filter.filter(exposes)

class AddressResolver(Processor):
    __log__ = logging.getLogger(__name__)
    
    def __init__(self, config):
        self.config = config
    
    def process_expose(self, expose):
        if expose['address'].startswith('http'):
            url = expose['address']
            for searcher in self.config.searchers():
                if re.search(searcher.URL_PATTERN, url):
                    expose['address'] = searcher.load_address(url)
                    self.__log__.debug("Loaded address %s for url %s" % (expose['address'], url))
                    break
        return expose

class LambdaProcessor(Processor):

    def __init__(self, config, func):
        self.func = func

    def process_expose(self, expose):
        res = self.func(expose)
        return expose
