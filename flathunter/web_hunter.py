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
                                        .apply_filter(filter) \
                                        .crawl_expose_details() \
                                        .save_all_exposes(self.id_watch) \
                                        .resolve_addresses() \
                                        .calculate_durations() \
                                        .build()

        new_exposes = []
        for expose in processor_chain.process(self.crawl_for_exposes(max_pages=1)):
            new_exposes.append(expose)

        for (user_id, settings) in self.id_watch.get_user_settings():
            if 'mute_notifications' in settings:
                continue
            filter = Filter.builder().read_config(settings).build()
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

    def get_exposes_since(self, datetime):
        return self.id_watch.get_exposes_since(datetime)

    def set_filters_for_user(self, user_id, filters):
        settings = self.id_watch.get_settings_for_user(user_id)
        if settings is None:
            settings = {}
        settings['filters'] = filters
        self.id_watch.save_settings_for_user(user_id, settings)

    def get_filters_for_user(self, user_id):
        settings = self.id_watch.get_settings_for_user(user_id)
        if settings is None:
            return None
        if 'filters' in settings:
            return settings['filters']
        return None

    def set_notification_status(self, user_id, receives_notifications):
        settings = self.id_watch.get_settings_for_user(user_id)
        if settings is None:
            if receives_notifications:
                return
            settings = {}
        if 'mute_notifications' in settings and receives_notifications:
            del settings['mute_notifications']
        if 'mute_notifications' not in settings and not receives_notifications:
            settings['mute_notifications'] = True
        self.id_watch.save_settings_for_user(user_id, settings)

    def toggle_notification_status(self, user_id):
        notifications_enabled = not self.notifications_muted_for_user(user_id)
        self.set_notification_status(user_id, not notifications_enabled)
        return not notifications_enabled

    def notifications_muted_for_user(self, user_id):
        settings = self.id_watch.get_settings_for_user(user_id)
        if settings is None:
            return False
        return ('mute_notifications' in settings)