class Processor:
    
    def process_exposes(self, exposes):
        return map(lambda e: self.process_expose(e), exposes)
