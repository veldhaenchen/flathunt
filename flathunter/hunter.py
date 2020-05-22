import logging
import requests
import re
import urllib.request
import urllib.parse
import urllib.error
import datetime
import time
from flathunter.sender_telegram import SenderTelegram


class Hunter:
    __log__ = logging.getLogger(__name__)
    GM_MODE_TRANSIT = 'transit'
    GM_MODE_BICYCLE = 'bicycling'
    GM_MODE_DRIVING = 'driving'

    def __init__(self, config, searchers, id_watch):
        self.config = config
        self.searchers = searchers
        self.id_watch = id_watch
        self.last_run = None
        self.excluded_titles = self.config.get('excluded_titles', list())

    def hunt_flats(self, connection=None):
        sender = SenderTelegram(self.config)
        new_exposes = []
        processed = self.id_watch.get(connection)

        for url in self.config.get('urls', list()):
            self.__log__.debug('Processing URL: ' + url)

            try:
                for searcher in self.searchers:
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

            for expose in results:
                # check if already processed
                if expose['id'] in processed:
                    continue

                self.__log__.info('New offer: ' + expose['title'])

                # to reduce traffic, some addresses need to be loaded on demand
                address = expose['address']
                if address.startswith('http'):
                    url = address
                    for searcher in self.searchers:
                        if re.search(searcher.URL_PATTERN, url):
                            address = searcher.load_address(url)
                            self.__log__.debug("Loaded address %s for url %s" % (address, url))
                            break

                # calculate durations if enabled
                durations_enabled = "google_maps_api" in self.config and self.config["google_maps_api"]["enable"]
                if durations_enabled:
                    durations = self.get_formatted_durations(self.config, address).strip()

                message = self.config.get('message', "").format(
                    title=expose['title'],
                    rooms=expose['rooms'],
                    size=expose['size'],
                    price=expose['price'],
                    url=expose['url'],
                    address=address,
                    durations="" if not durations_enabled else durations).strip()

                # if no excludes, send messages
                if len(self.excluded_titles) == 0:
                    # send message to all receivers
                    sender.send_msg(message)
                    new_exposes.append(expose)
                    self.id_watch.add(expose['id'], connection)
                    continue

                # combine all the regex patterns into one
                combined_excludes = "(" + ")|(".join(self.excluded_titles) + ")"
                found_objects = re.search(combined_excludes, expose['title'].lower())
                # send all non matching regex patterns
                if not found_objects:
                    # send message to all receivers
                    sender.send_msg(message)
                    new_exposes.append(expose)
                    self.id_watch.add(expose['id'], connection)

        self.__log__.info(str(len(new_exposes)) + ' new offers found')
        self.last_run = datetime.datetime.now()
        return new_exposes

    def get_formatted_durations(self, config, address):
        out = ""
        for duration in config.get('durations', list()):
            if 'destination' in duration and 'name' in duration:
                dest = duration.get('destination')
                name = duration.get('name')
                for mode in duration.get('modes', list()):
                    if 'gm_id' in mode and 'title' in mode and 'key' in config.get('google_maps_api', dict()):
                        duration = self.get_gmaps_distance(config, address, dest, mode['gm_id'])
                        out += "> %s (%s): %s\n" % (name, mode['title'], duration)

        return out.strip()

    def get_gmaps_distance(self, config, address, dest, mode):
        # get timestamp for next monday at 9:00:00 o'clock
        now = datetime.datetime.today().replace(hour=9, minute=0, second=0)
        next_monday = now + datetime.timedelta(days=(7 - now.weekday()))
        arrival_time = str(int(time.mktime(next_monday.timetuple())))

        # decode from unicode and url encode addresses
        address = urllib.parse.quote_plus(address.strip().encode('utf8'))
        dest = urllib.parse.quote_plus(dest.strip().encode('utf8'))
        self.__log__.debug("Got address: %s" % address)

        # get google maps config stuff
        base_url = config.get('google_maps_api', dict()).get('url')
        gm_key = config.get('google_maps_api', dict()).get('key')

        if not gm_key and mode != self.GM_MODE_DRIVING:
            self.__log__.warning("No Google Maps API key configured and without using a mode different from "
                                 "'driving' is not allowed. Downgrading to mode 'drinving' thus. ")
            mode = 'driving'
            base_url = base_url.replace('&key={key}', '')

        # retrieve the result
        url = base_url.format(dest=dest, mode=mode, origin=address, key=gm_key, arrival=arrival_time)
        result = requests.get(url).json()
        if result['status'] != 'OK':
            self.__log__.error("Failed retrieving distance to address %s: " % address, result)
            return None

        # get the fastest route
        distances = dict()
        for row in result['rows']:
            for element in row['elements']:
                if 'status' in element and element['status'] != 'OK':
                    self.__log__.warning("For address %s we got the status message: %s" % (address, element['status']))
                    self.__log__.debug("We got this result: %s" % repr(result))
                    continue
                self.__log__.debug("Got distance and duration: %s / %s (%i seconds)"
                                   % (element['distance']['text'], element['duration']['text'],
                                      element['duration']['value'])
                                   )
                distances[element['duration']['value']] = '%s (%s)' % \
                                                          (element['duration']['text'], element['distance']['text'])
        return distances[min(distances.keys())] if distances else None
