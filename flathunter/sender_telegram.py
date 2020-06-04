import urllib.request, urllib.parse, urllib.error
import requests
import logging

from flathunter.abstract_processor import Processor

class SenderTelegram(Processor):
    __log__ = logging.getLogger(__name__)

    def __init__(self, config):
        self.config = config
        self.bot_token = self.config.get('telegram', dict()).get('bot_token', '')
        self.receiver_ids = self.config.get('telegram', dict()).get('receiver_ids', list())

    def process_expose(self, expose):
        message = self.config.get('message', "").format(
            title=expose['title'],
            rooms=expose['rooms'],
            size=expose['size'],
            price=expose['price'],
            url=expose['url'],
            address=expose['address'],
            durations="" if 'durations' not in expose else expose['durations']).strip()
        self.send_msg(message)
        return expose

    def send_msg(self, message):
        if self.receiver_ids is None:
            return
        for chat_id in self.receiver_ids:
            url = 'https://api.telegram.org/bot%s/sendMessage?chat_id=%i&text=%s'
            text = urllib.parse.quote_plus(message.encode('utf-8'))
            self.__log__.debug(('token:', self.bot_token))
            self.__log__.debug(('chatid:', chat_id))
            self.__log__.debug(('text', text))
            qry = url % (self.bot_token, chat_id, text)
            self.__log__.debug("Retrieving URL %s" % qry)
            resp = requests.get(qry)
            self.__log__.debug("Got response (%i): %s" % (resp.status_code, resp.content))
            data = resp.json()

            # handle error
            if resp.status_code != 200:
                sc = resp.status_code
                self.__log__.error("When sending bot message, we got status %i with message: %s" % (sc, data))
