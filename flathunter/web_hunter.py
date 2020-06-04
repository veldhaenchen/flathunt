import logging
import datetime

from flathunter.hunter import Hunter

class WebHunter(Hunter):
    __log__ = logging.getLogger(__name__)

    def hunt_flats(self):
        new_exposes = super().hunt_flats()
                
        self.id_watch.update_last_run_time()
        return new_exposes

    def get_last_run_time(self):
        return self.id_watch.get_last_run_time()

    def get_recent_exposes(self, count=9):
        return self.id_watch.get_recent_exposes(count)