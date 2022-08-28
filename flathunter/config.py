"""Wrap configuration options as an object"""
import os
import yaml

from dotenv import load_dotenv

from flathunter.logging import logger
from flathunter.captcha.imagetyperz_solver import ImageTyperzSolver
from flathunter.captcha.twocaptcha_solver import TwoCaptchaSolver
from flathunter.captcha.captcha_solver import CaptchaSolver
from flathunter.crawl_ebaykleinanzeigen import CrawlEbayKleinanzeigen
from flathunter.crawl_immobilienscout import CrawlImmobilienscout
from flathunter.crawl_wggesucht import CrawlWgGesucht
from flathunter.crawl_immowelt import CrawlImmowelt
from flathunter.crawler_subito import CrawlSubito
from flathunter.crawl_immobiliare import CrawlImmobiliare
from flathunter.crawl_idealista import CrawlIdealista
from flathunter.filter import Filter

load_dotenv()

class Env:

    def readenv(key):
        if key in os.environ:
            return os.environ[key]
        return None

    # Captcha setup
    FLATHUNTER_2CAPTCHA_KEY = readenv("FLATHUNTER_2CAPTCHA_KEY")
    FLATHUNTER_IMAGETYPERZ_TOKEN = readenv("FLATHUNTER_IMAGETYPERZ_TOKEN")

    # Generic Config
    FLATHUNTER_TARGET_URLS = readenv("FLATHUNTER_TARGET_URLS")
    FLATHUNTER_DATABASE_LOCATION = readenv("FLATHUNTER_DATABASE_LOCATION")
    FLATHUNTER_VERBOSE_LOG = readenv("FLATHUNTER_VERBOSE_LOG")
    FLATHUNTER_LOOP_PERIOD_SECONDS = readenv("FLATHUNTER_LOOP_PERIOD_SECONDS")

    # Website setup
    FLATHUNTER_WEBSITE_SESSION_KEY = readenv("FLATHUNTER_WEBSITE_SESSION_KEY")
    FLATHUNTER_WEBSITE_DOMAIN = readenv("FLATHUNTER_WEBSITE_DOMAIN")

class Config:
    """Class to represent flathunter configuration"""

    def __init__(self, filename=None, string=None):
        self.useEnvironment = True
        if string is not None:
            self.config = yaml.safe_load(string)
            self.useEnvironment = False
        else:
            if filename is None and Env.FLATHUNTER_TARGET_URLS is None:
                raise Exception("Config file loaction must be specified, or FLATHUNTER_TARGET_URLS must be set")
            if filename is not None:
                logger.info("Using config path %s", filename)
                if not os.path.exists(filename):
                    raise Exception("No config file found at location %s")
                with open(filename, encoding="utf-8") as file:
                    self.config = yaml.safe_load(file)
            else:
                self.config = {}
        self.__searchers__ = []
        self.check_deprecated()

    def __iter__(self):
        """Emulate dictionary"""
        return self.config.__iter__()

    def __getitem__(self, value):
        """Emulate dictionary"""
        return self.config[value]

    def init_searchers(self):
        """Initialize search plugins"""
        self.__searchers__ = [
            CrawlImmobilienscout(self),
            CrawlWgGesucht(self),
            CrawlEbayKleinanzeigen(self),
            CrawlImmowelt(self),
            CrawlSubito(self),
            CrawlImmobiliare(self),
            CrawlIdealista(self)
        ]

    def check_deprecated(self):
        """Notifies user of deprecated config items"""
        captcha_config = self.config.get("captcha")
        if captcha_config is not None:
            if captcha_config.get("imagetypers") is not None:
                logger.warning(
                    'Captcha configuration for "imagetypers" (captcha/imagetypers) has been '
                    'renamed to "imagetyperz". '
                    'We found an outdated entry, which has to be renamed accordingly, in order '
                    'to be detected again.'
                )
            if captcha_config.get("driver_path") is not None:
                logger.warning(
                    'Captcha configuration for "driver_path" (captcha/driver_path) is no longer '
                    'required, as driver setup has been automated.'
                )

    def get(self, key, value=None):
        """Emulate dictionary"""
        return self.config.get(key, value)

    def _read_yaml_path(self, path, default_value=None):
        config = self.config
        parts = path.split('.')
        while len(parts) > 1:
            config = config.get(parts[0], {})
            parts = parts[1:]
        return config.get(parts[0], default_value)

    def database_location(self):
        """Return the location of the database folder"""
        config_database_location = self._read_yaml_path('database_location')
        if config_database_location is not None:
            return config_database_location
        if self.useEnvironment and Env.FLATHUNTER_DATABASE_LOCATION is not None:
            return Env.FLATHUNTER_DATABASE_LOCATION
        return os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/..")

    def set_searchers(self, searchers):
        """Update the active search plugins"""
        self.__searchers__ = searchers

    def searchers(self):
        """Get the list of search plugins"""
        return self.__searchers__

    def get_filter(self):
        """Read the configured filter"""
        builder = Filter.builder()
        builder.read_config(self.config)
        return builder.build()

    def target_urls(self):
        if self.useEnvironment and Env.FLATHUNTER_TARGET_URLS is not None:
            return Env.FLATHUNTER_TARGET_URLS.split(';')
        return self._read_yaml_path('urls', [])

    def verbose_logging(self):
        if self.useEnvironment and Env.FLATHUNTER_VERBOSE_LOG is not None:
            return True
        return self._read_yaml_path('verbose') is not None

    def loop_is_active(self):
        if self.useEnvironment and Env.FLATHUNTER_LOOP_PERIOD_SECONDS is not None:
            return True
        return self._read_yaml_path('loop.active', False)

    def loop_period_seconds(self):
        if self.useEnvironment and Env.FLATHUNTER_LOOP_PERIOD_SECONDS is not None:
            return int(Env.FLATHUNTER_LOOP_PERIOD_SECONDS)
        return self._read_yaml_path('loop.sleeping_time', 60 * 10)

    def has_website_config(self):
        if self.useEnvironment and Env.FLATHUNTER_WEBSITE_SESSION_KEY is not None:
            return True
        return 'website' in self.config

    def website_session_key(self):
        if self.useEnvironment and Env.FLATHUNTER_WEBSITE_SESSION_KEY is not None:
            return Env.FLATHUNTER_WEBSITE_SESSION_KEY
        return self._read_yaml_path('website.session_key', None)

    def website_domain(self):
        if self.useEnvironment and Env.FLATHUNTER_WEBSITE_DOMAIN is not None:
            return Env.FLATHUNTER_WEBSITE_DOMAIN
        return self._read_yaml_path('website.domain', None)

    def website_bot_name(self):
        if self.useEnvironment and Env.FLATHUNTER_WEBSITE_BOT_NAME is not None:
            return Env.FLATHUNTER_WEBSITE_BOT_NAME
        return self._read_yaml_path('website.bot_name', None)

    def captcha_enabled(self):
        """Check if captcha is configured"""
        return "captcha" in self.config

    def get_captcha_solver(self) -> CaptchaSolver:
        """Get configured captcha solver"""
        if self.useEnvironment and Env.FLATHUNTER_IMAGETYPERZ_TOKEN is not None:
            imagetyperz_token = Env.FLATHUNTER_IMAGETYPERZ_TOKEN
        else:
            imagetyperz_token = self._read_yaml_path("captcha.imagetyperz.token", "")
        if imagetyperz_token:
            return ImageTyperzSolver(imagetyperz_token)

        if self.useEnvironment and Env.FLATHUNTER_2CAPTCHA_KEY is not None:
            twocaptcha_api_key = Env.FLATHUNTER_2CAPTCHA_KEY
        else:
            twocaptcha_api_key = self._read_yaml_path("captcha.2captcha.api_key", "")
        if twocaptcha_api_key:
            return TwoCaptchaSolver(twocaptcha_api_key)

        raise Exception("No captcha solver configured properly.")


    def use_proxy(self):
        """Check if proxy is configured"""
        return "use_proxy_list" in self.config and self.config["use_proxy_list"]
