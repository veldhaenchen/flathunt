import logging
import datetime

from flathunter.hunter import Hunter
from flathunter.filter import Filter
from flathunter.processor import ProcessorChain

class WebHunter(Hunter):
    __log__ = logging.getLogger(__name__)

    def hunt_flats(self):
        filter = Filter.builder() \
                       .filter_already_seen(self.id_watch) \
                       .build()

        processor_chain = ProcessorChain.builder(self.config) \
                                        .crawl_expose_details() \
                                        .save_all_exposes(self.id_watch) \
                                        .apply_filter(filter) \
                                        .resolve_addresses() \
                                        .calculate_durations() \
                                        .build()

        new_exposes = processor_chain.process(self.crawl_for_exposes(max_pages=1))

        for (user_id, filters) in self.id_watch.get_user_filters():
            filter = Filter.builder().read_config({ 'filters': filters }).build()
            processor_chain = ProcessorChain.builder(self.config) \
                                            .apply_filter(filter) \
                                            .send_telegram_messages([ user_id ]) \
                                            .build()
            for message in processor_chain.process(new_exposes):
                self.__log__.debug("Sent expose " + str(message['id']) + " to user " + str(user_id))

        self.id_watch.update_last_run_time()
        return list(new_exposes)

    def get_last_run_time(self):
        return self.id_watch.get_last_run_time()

    def get_recent_exposes(self, count=9, filter=None):
        return self.id_watch.get_recent_exposes(count, filter=filter)

    def set_filters_for_user(self, user_id, filters):
        self.id_watch.set_filters_for_user(user_id, filters)

    def get_filters_for_user(self, user_id):
        return self.id_watch.get_filters_for_user(user_id)
