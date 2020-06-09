import logging
import re
from functools import reduce

from flathunter.default_processors import AddressResolver
from flathunter.default_processors import Filter
from flathunter.default_processors import LambdaProcessor
from flathunter.sender_telegram import SenderTelegram
from flathunter.gmaps_duration_processor import GMapsDurationProcessor
from flathunter.idmaintainer import SaveAllExposesProcessor

class ProcessorChainBuilder:
    
    def __init__(self, config):
        self.processors = []
        self.config = config
        
    def send_telegram_messages(self, receivers=None):
        self.processors.append(SenderTelegram(self.config, receivers=receivers))
        return self
        
    def resolve_addresses(self):
        self.processors.append(AddressResolver(self.config))
        return self
    
    def calculate_durations(self):
        # calculate durations if enabled
        durations_enabled = "google_maps_api" in self.config and self.config["google_maps_api"]["enable"]
        if durations_enabled:
            self.processors.append(GMapsDurationProcessor(self.config))
        return self

    def map(self, func):
        self.processors.append(LambdaProcessor(self.config, func))
        return self
    
    def apply_filter(self, filter):
        self.processors.append(Filter(self.config, filter))
        return self

    def save_all_exposes(self, id_watch):
        self.processors.append(SaveAllExposesProcessor(self.config, id_watch))
        return self
        
    def build(self):
        return ProcessorChain(self.processors)

class ProcessorChain:
    
    def __init__(self, processors):
        self.processors = processors
    
    def process(self, exposes):
        return reduce((lambda exposes, processor: processor.process_exposes(exposes)), self.processors, exposes)
            
    @staticmethod
    def builder(config):
        return ProcessorChainBuilder(config)