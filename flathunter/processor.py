import logging
import re

class Processor:
    
    def process_exposes(self, exposes):
        return map(lambda e: self.process_expose(e), exposes)

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
                print("Comparing %s with %s", (searcher.URL_PATTERN, url))
                if re.search(searcher.URL_PATTERN, url):
                    expose['address'] = searcher.load_address(url)
                    self.__log__.debug("Loaded address %s for url %s" % (expose['address'], url))
                    break
        return expose
    
class DurationResolver:
    
    pass

class TelegramNotifier:
    
    pass

class ProcessorChainBuilder:
    
    def __init__(self, config):
        self.processors = []
        self.config = config
        
    def telegram_notifier(self):
        self.processors.append(TelegramNotifier(self.config))
        return self
        
    def resolve_addresses(self):
        self.processors.append(AddressResolver(self.config))
        return self
    
    def apply_filter(self, filter):
        self.processors.append(Filter(self.config, filter))
        return self
        
    def build(self):
        return ProcessorChain(self.processors)

class ProcessorChain:
    
    def __init__(self, processors):
        self.processors = processors
    
    def process(self, exposes):
        for processor in self.processors:
            exposes = processor.process_exposes(exposes)
        return exposes
            
    @staticmethod
    def builder(config):
        return ProcessorChainBuilder(config)