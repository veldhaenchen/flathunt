import requests
import backoff
from dataclasses import dataclass

@dataclass
class GeetestResponse:
    challenge: str
    validate: str
    secCode: str

@dataclass
class RecaptchaResponse:
    result: str


class CaptchaSolver:
    backoff_options = {
        "wait_gen":backoff.constant,
        "exception":requests.exceptions.RequestException,
        "max_time":100
    }

    def __init__(self, api_key):
        self.api_key = api_key

    def solve_geetest(self, gt: str, challenge: str, page_url: str) -> GeetestResponse:
        raise NotImplementedError()

    def solve_recaptcha(self, google_site_key: str, page_url: str) -> RecaptchaResponse:
        raise NotImplementedError()

class CaptchaUnsolvableError(Exception):
    def __init__(self):
        self.message = "Failed to solve captcha."
    pass

