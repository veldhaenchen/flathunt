"""
Create or edit a basic flathunter configuration
"""
import sys
import re
from typing import List, Any, Dict
from enum import Enum

from prompt_toolkit.shortcuts import message_dialog, input_dialog, radiolist_dialog, clear
from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator, ValidationError

from flathunter.config import Config

class ConfigurationAborted(Exception):
    def __str__(self):
        return "Configuration Aborted"

class ConfigurationError(Exception):
    pass

class Notifier(Enum):
    TELEGRAM = "telegram"
    MATTERMOST = "mattermost"
    APPRISE = "apprise"

def welcome():
    message_dialog(
        title="Flathunter Configuration Wizard",
        text="Welcome to the Flathunter Configuration Wizard\n\n"
          "This Wizard will take you through the configuration of your Flathunter\ninstallation. "
          "The configuration generated will be saved to\n"
          "  `config.yaml` or `.env`\n"
          "in your project directory (depending on your selections)\n\n"
          "Press ENTER to continue.",
    ).run()

class UrlsValidator(Validator):
    def __init__(self, urls, config):
        self.urls = urls
        self.config = config

    def validate(self, document: Document):
        if len(document.text) == 0:
            if len(self.urls) == 0:
                raise ValidationError(cursor_position=0, message="Supply at least one URL")
            return
        for searcher in self.config.searchers():
            if re.search(searcher.URL_PATTERN, document.text):
                return
        raise ValidationError(cursor_position=len(document.text), message="URL did not match any configured scraper")


def gather_urls() -> List[str]:
    urls = []
    result = None
    config = Config()
    config.init_searchers()
    while len(urls) == 0 or len(result) > 0:
        clear()
        print("Enter URLs for Scraping\n")
        print("Flathunter scrapes property portals by fetching content from search URLs\n"
            "on the websites. Visit ImmoScout, ImmoWelt, eBay-Kleinanzeigen or WG-Gesucht,\n"
            "make a search for the flat that you are looking for (e.g. pick a city), and\n"
            "copy the URL here. You can add as many URLs as you like.\n\n")
        if len(urls) > 0:
            print("\n".join(urls))
            print("")
        result = prompt("Enter a target URL (or hit enter to continue): ",
            validator=UrlsValidator(urls, config), validate_while_typing=False)
        if len(result) > 0:
            urls.append(result)
        if len(result) == 0 and len(urls) == 0:
            raise ConfigurationAborted()
    return urls

def select_notifier() -> str:
    return radiolist_dialog(
        values=[
            (Notifier.TELEGRAM.value, "Telegram"),
            (Notifier.MATTERMOST.value, "Mattermost"),
            (Notifier.APPRISE.value, "Apprise"),
        ],
        title="Configure notifications",
        text="Choose a notification platform.",
    ).run()

def get_bot_token() -> str:
    clear()
    print("Telegram Bot Token\n")
    print("To send Telegram messages, we need a Telegram Bot Token. You can follow\n"
        "the instructions here to track down 'The BotFather' and generate your token:\n"
        "https://medium.com/geekculture/generate-telegram-token-for-bot-api-d26faf9bf064\n")

    result = prompt("Enter Bot Token: ")
    if result is None or len(result) == 0:
        raise ConfigurationAborted()
    return result

def get_receiver_id() -> str:
    clear()
    print("Telegram Receiver ID\n")
    print("Your Telegram Bot needs to know which user to send the notifications to.\n"
        "This will normally be the User ID associated with your Telegram Account.\n"
        "To work out your User ID, start a chat with the @userinfobot:\n"
        "https://telegram.me/userinfobot\n")
    result = prompt("Enter Receiver ID: ")
    if len(result) == 0:
        raise ConfigurationAborted()
    return result

def configure_telegram() -> Dict[str, Any]:
    bot_token = get_bot_token()
    receiver_id = get_receiver_id()
    return {
        Notifier.TELEGRAM.value: {
            "bot_token": bot_token,
            "receiver_ids": [ receiver_id ]
        }
    }

def configure_mattermost() -> Dict[str, Any]:
    clear()
    print("Mattermost Webhook URL\n")
    print("To receive messages over Mattermost, Flathunter will need the Webhook URL\n"
    "of your Mattermost server.\n")
    webhook_url = prompt("Enter Webhook URL: ")
    if len(webhook_url) == 0:
        raise ConfigurationAborted()
    return {
        Notifier.MATTERMOST.value: {
            "webhook_url": webhook_url
        }
    }

def configure_apprise() -> Dict[str, Any]:
    clear()
    print("Apprise notification URL\n")
    print("To receive messages using Apprise, you need to supply a notification URL in the\n"
    "apprise format, e.g. 'gotifys://...' or 'mailto://...'\n")
    apprise_url = prompt("Enter Apprise notification URL: ")
    if len(apprise_url) == 0:
        raise ConfigurationAborted()
    return {
        Notifier.APPRISE.value: [ apprise_url ]
    }

def configure_notifier(notifier: str) -> Dict[str, Any]:
    if notifier == Notifier.TELEGRAM.value:
        return configure_telegram()
    if notifier == Notifier.MATTERMOST.value:
        return configure_mattermost()
    if notifier == Notifier.APPRISE.value:
        return configure_apprise()
    raise ConfigurationError("Invalid Notifier Selection")

def main():
    try:
        welcome()
        gather_urls()
        notifier = select_notifier()
        configure_notifier(notifier)
    except ConfigurationAborted:
        print("Configuration was aborted by user action")
        sys.exit(1)


if __name__ == "__main__":
    main()
