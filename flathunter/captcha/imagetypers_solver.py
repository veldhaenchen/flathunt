import json
import logging
from typing import Dict
from time import sleep as sleep

import backoff
import requests

from flathunter.captcha.captcha_solver import (
    CaptchaSolver,
    CaptchaUnsolvableError,
    GeetestResponse,
    RecaptchaResponse,
)

logger = logging.getLogger('flathunt')

class ImageTypersSolver(CaptchaSolver):
    def solve_geetest(self, gt: str, challenge: str, page_url: str) -> GeetestResponse:
        logger.info("Trying to solve geetest.")
        params = {
            "action": "UPLOADCAPTCHA",
            "domain": page_url,
            "challenge": challenge,
            "gt": gt,
            "token": self.api_key,
        }
        captcha_id = self.__submit_imagetypers_request(
            "http://www.captchatypers.com/captchaapi/UploadGeeTestToken.ashx",
            params
        )
        result = self.__retrieve_imagetypers_result(captcha_id)

        # imagetypers sometimes returns a json object, and sometimes a ';;;;'-seperated list
        # one can only assume that the empolyees type in the webserver response by hand
        try:
            untyped_result = json.loads(result)
            return GeetestResponse(untyped_result["geetest_challenge"],
                                   untyped_result["geetest_validate"],
                                   untyped_result["geetest_seccode"])
        except json.decoder.JSONDecodeError:
            parts = result.split(";;;")
            return GeetestResponse(parts[0], parts[1], parts[2])


    def solve_recaptcha(self, google_site_key: str, page_url: str) -> RecaptchaResponse:
        logger.info("Trying to solve recaptcha.")
        params = {
            "action": "UPLOADCAPTCHA",
            "pageurl": page_url,
            "googlekey": google_site_key,
            "token": self.api_key,
        }
        captcha_id = self.__submit_imagetypers_request(
            "http://www.captchatypers.com/captchaapi/UploadRecaptchaToken.ashx",
             params
        )
        return RecaptchaResponse(self.__retrieve_imagetypers_result(captcha_id))


    @backoff.on_exception(**CaptchaSolver.backoff_options)
    def __submit_imagetypers_request(self, submit_url: str, params: Dict[str, str]) -> str:
        submit_response = requests.get(submit_url, params=params)
        logger.debug("Got response from imagetypers/request: %s:", submit_response.text)

        if "error" in submit_response.text.lower():
            raise requests.HTTPError(response=submit_response)


        return submit_response.text


    @backoff.on_exception(**CaptchaSolver.backoff_options)
    def __retrieve_imagetypers_result(self, captcha_id: str):
        retrieve_url = (
            f"http://www.captchatypers.com/captchaapi/GetCaptchaResponseJson.ashx"
        )
        params = {
            "action": "GETTEXT",
            "token": self.api_key,
            "captchaid": captcha_id,
        }

        while True:
            retrieve_response = requests.get(retrieve_url, params=params)
            logger.debug("Got response from imagetypers: %s:", retrieve_response.text)
            response = json.loads(retrieve_response.text)[0]
            if response["Status"] == "Pending":
                logger.info("Captcha is not ready yet, waiting...")
                sleep(5)
                continue

            if response["Status"] == "ERROR: IMAGE_TIMED_OUT":
                raise CaptchaUnsolvableError()
            elif not response["Status"] == "Solved":
                raise requests.HTTPError(response=retrieve_response)

            return response["Response"]
