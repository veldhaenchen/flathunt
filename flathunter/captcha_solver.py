import requests
import backoff
import logging
from time import sleep as sleep

logger = logging.getLogger('flathunt')

def solve_geetest(api_key: str, gt: str, challenge: str, page_url: str) -> str:
    logger.debug("Trying to solve geetest.")
    submit_url = (
        f"http://2captcha.com/in.php?key={api_key}&method=geetest" +
        f"&gt={gt}&challenge={challenge}&api_server=api.geetest.com&pageurl={page_url}"
    )
    captcha_id = __submit_2captcha_request(submit_url)
    return __retrieve_2captcha_result(api_key, captcha_id)

def solve_recaptcha(api_key: str, google_site_key: str, page_url: str) -> str:
    logger.debug("Trying to solve 2captcha.")
    submit_url = (
        f"http://2captcha.com/in.php?key={api_key}&method=userrecaptcha" +
        f"&googlekey={google_site_key}&pageurl={page_url}"
    )
    captcha_id = __submit_2captcha_request(submit_url)
    return __retrieve_2captcha_result(api_key, captcha_id)

@backoff.on_exception(wait_gen=backoff.constant,
                      exception=requests.exceptions.RequestException,
                      max_time=100)
def __submit_2captcha_request(submit_url: str) -> str:
    submit_response = requests.post(submit_url)

    if not submit_response.text.startswith("OK"):
        raise requests.HTTPError(response=submit_response)

    return submit_response.text.split("|")[1]


@backoff.on_exception(wait_gen=backoff.constant,
                      exception=requests.exceptions.RequestException,
                      max_time=100)
def __retrieve_2captcha_result(api_key: str, captcha_id: str) -> str:
    retrieve_url = f"http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}"
    while True:
        retrieve_response = requests.get(retrieve_url)
        if "CAPCHA_NOT_READY" in retrieve_response.text:
            logger.debug("Captcha is not ready yet, waiting...")
            sleep(5)
            continue

        if "ERROR_CAPTCHA_UNSOLVABLE" in retrieve_response.text:
            raise CaptchaUnsolvableError()
        elif not retrieve_response.text.startswith("OK"):
            logger.debug("Got error response from 2captcha: %s", retrieve_response.text)
            raise requests.HTTPError()

        return retrieve_response.text.split("|", 1)[1]

class CaptchaUnsolvableError(Exception):
    pass
