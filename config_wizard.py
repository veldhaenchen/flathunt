"""
Create or edit a basic flathunter configuration
"""
import sys
import re
import os
from typing import List, Any, Dict, Optional
from enum import Enum
from functools import reduce

from ruamel.yaml import YAML
from prompt_toolkit.shortcuts import message_dialog, input_dialog,\
    radiolist_dialog, clear, button_dialog
from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator, ValidationError

from flathunter.config import Config, YamlConfig
import flathunter.crawl_immobilienscout as crawl_immobilienscout

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
          "The configuration generated will be saved to `config.yaml`\n"
          "in your project directory\n\n"
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


def gather_urls(config: Config) -> List[str]:
    urls = config.target_urls()
    result = ""
    first_run = True
    while first_run or len(urls) == 0 or len(result) > 0:
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
        first_run = False
    return urls

def select_notifier(config: Config) -> str:
    if len(config.notifiers()) > 0:
        default = config.notifiers()[0]
    else:
        default = Notifier.TELEGRAM.value
    return radiolist_dialog(
        values=[
            (Notifier.TELEGRAM.value, "Telegram"),
            (Notifier.MATTERMOST.value, "Mattermost"),
            (Notifier.APPRISE.value, "Apprise"),
        ],
        title="Configure notifications",
        text="Choose a notification platform.",
        default=default
    ).run()

def get_bot_token(config: Config) -> str:
    clear()
    print("Telegram Bot Token\n")
    print("To send Telegram messages, we need a Telegram Bot Token. You can follow\n"
        "the instructions here to track down 'The BotFather' and generate your token:\n"
        "https://medium.com/geekculture/generate-telegram-token-for-bot-api-d26faf9bf064\n")

    if config.telegram_bot_token() is not None:
        result = prompt("Enter Bot Token: ", default = config.telegram_bot_token())
    else:
        result = prompt("Enter Bot Token: ")

    if result is None or len(result) == 0:
        raise ConfigurationAborted()
    return result

def get_receiver_id(config: Config) -> str:
    clear()
    print("Telegram Receiver ID\n")
    print("Your Telegram Bot needs to know which user to send the notifications to.\n"
        "This will normally be the User ID associated with your Telegram Account.\n"
        "To work out your User ID, start a chat with the @userinfobot:\n"
        "https://telegram.me/userinfobot\n")
    if len(config.telegram_receiver_ids()) > 0:
        result = prompt("Enter Receiver ID: ", default = config.telegram_receiver_ids()[0])
    else:
        result = prompt("Enter Receiver ID: ")

    if len(result) == 0:
        raise ConfigurationAborted()
    return result

def configure_telegram(config: Config) -> Dict[str, Any]:
    bot_token = get_bot_token(config)
    receiver_id = get_receiver_id(config)
    return {
        Notifier.TELEGRAM.value: {
            "bot_token": bot_token,
            "receiver_ids": [ receiver_id ]
        }
    }

def configure_mattermost(config: Config) -> Dict[str, Any]:
    clear()
    print("Mattermost Webhook URL\n")
    print("To receive messages over Mattermost, Flathunter will need the Webhook URL\n"
    "of your Mattermost server.\n")
    if config.mattermost_webhook_url() is not None:
        webhook_url = prompt("Enter Webhook URL: ", default=config.mattermost_webhook_url())
    else:
        webhook_url = prompt("Enter Webhook URL: ")

    if len(webhook_url) == 0:
        raise ConfigurationAborted()
    return {
        Notifier.MATTERMOST.value: {
            "webhook_url": webhook_url
        }
    }

def configure_apprise(config: Config) -> Dict[str, Any]:
    clear()
    print("Apprise notification URL\n")
    print("To receive messages using Apprise, you need to supply a notification URL in the\n"
    "apprise format, e.g. 'gotifys://...' or 'mailto://...'\n")
    if len(config.apprise_urls()) > 0:
        apprise_url = prompt("Enter Apprise notification URL: ", config.apprise_urls()[0])
    else:
        apprise_url = prompt("Enter Apprise notification URL: ")

    if len(apprise_url) == 0:
        raise ConfigurationAborted()
    return {
        Notifier.APPRISE.value: [ apprise_url ]
    }

def configure_notifier(notifier: str, config) -> Dict[str, Any]:
    if notifier == Notifier.TELEGRAM.value:
        return configure_telegram(config)
    if notifier == Notifier.MATTERMOST.value:
        return configure_mattermost(config)
    if notifier == Notifier.APPRISE.value:
        return configure_apprise(config)
    raise ConfigurationError("Invalid Notifier Selection")

def configure_captcha(urls: List[str], config: Config) -> Optional[Dict[str, Any]]:
    is_immoscout = reduce(lambda a,b: a or b,
        [ re.search(crawl_immobilienscout.STATIC_URL_PATTERN, url) for url in urls ],
        False)
    if not is_immoscout:
        return None
    clear()
    print("Captcha configuration\n")
    print("Your search configuration includes URLs from ImmobilienScout24\n"
    "To crawl ImmoScout, we need to browse the site with a real Chrome browser instance\n"
    "and solve the Captcha that shows up on the ImmoScout site.\n")
    print("We recommend using 2captcha (https://2captcha.com/) as your captcha-solving\n"
    "service. You will need an account there with some credit on it.\n"
    "IMPORTANT NOTICE: Buying captcha credit does not guarantee that Flathunter will be\n"
    "able to bypass the bot detection on the ImmoScout site - pay at your own risk!!\n")
    print("Once you have an account and have paid, enter the API Key here (or hit Enter\n"
    "to skip Captcha configuration, but be aware that ImmoScout scraping will fail...)\n")
    if config.get_twocaptcha_key() is not None:
        api_key = prompt("Enter 2Captcha API Key: ", default=config.get_twocaptcha_key())
    else:
        api_key = prompt("Enter 2Captcha API Key: ")

    if len(api_key) == 0:
        return None
    return {
        "captcha": {
            "2captcha": {
                "api_key": api_key
            },
            "driver_arguments": [
              "--no-sandbox",
              "--headless",
              "--disable-gpu",
              "--remote-debugging-port=9222",
              "--disable-dev-shm-usage",
              "window-size=1024,768"
            ]
        }
    }

def load_config(existing):
    yaml = YAML()
    source_file = "config.yaml.dist"
    if existing:
        source_file = "config.yaml"
    with open(source_file, "r") as dist_config:
        config = yaml.load(dist_config)
    return YamlConfig(config)

def save_config(config: Dict):
    clear()
    yaml = YAML()
    with open("config.yaml", "w") as config_file:
        yaml.dump(config, config_file)
    print("Configuration saved to 'config.yaml' - you're all set!")

def check_existing():
    if not os.path.exists("config.yaml"):
        return False
    result = button_dialog(
        title="Config File Exists",
        text="We found an existing 'config.yaml' file in the current directory\n"
        "Running the wizard will update / edit this file. Do you want to proceed?",
        buttons=[("Yes", True), ("No", False)],
    ).run()
    if not result:
        raise ConfigurationAborted()
    return True


def main():
    try:
        welcome()
        existing = check_existing()
        config = load_config(existing)
        config.init_searchers()
        urls = gather_urls(config)
        config.set_keys({ "urls": urls })
        notifier = select_notifier(config)
        config.set_keys({ "notifiers": [ notifier ]})
        notifier_config = configure_notifier(notifier, config)
        config.set_keys(notifier_config)
        captcha_config = configure_captcha(urls, config)
        if captcha_config is not None:
            config.set_keys(captcha_config)
        save_config(config.config)
    except ConfigurationAborted:
        print("Configuration was aborted by user action")
        sys.exit(1)


if __name__ == "__main__":
    main()
