import subprocess
import undetected_chromedriver.v2 as uc

from flathunter.logging import logger

def get_chrome_version():
    for binary_name in ['google-chrome', 'chromium', 'chrome']:
        try:
            return subprocess.Popen([binary_name, '--version'],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        universal_newlines=True).stdout.readline().split(' '
                    )[2].split('.')[0]
        except FileNotFoundError:
            pass
    return None

def get_chrome_driver(driver_arguments):
    """Configure Chrome WebDriver"""
    logger.info('Initializing Chrome WebDriver for crawler...')
    chrome_options = uc.ChromeOptions() # pylint: disable=no-member
    if driver_arguments is not None:
        for driver_argument in driver_arguments:
            chrome_options.add_argument(driver_argument)
    chrome_version = get_chrome_version()
    driver = uc.Chrome(version_main=chrome_version, options=chrome_options) # pylint: disable=no-member

    driver.execute_cdp_cmd('Network.setBlockedURLs',
        {"urls": ["https://api.geetest.com/get.*"]})
    driver.execute_cdp_cmd('Network.enable', {})
    return driver
