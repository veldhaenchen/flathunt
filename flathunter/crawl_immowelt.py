"""Expose crawler for ImmoWelt"""
import logging
import re
import datetime

from flathunter.abstract_crawler import Crawler

class CrawlImmowelt(Crawler):
    """Implementation of Crawler interface for ImmoWelt"""

    __log__ = logging.getLogger('flathunt')
    URL_PATTERN = re.compile(r'https://www\.immowelt\.de')

    def __init__(self, config):
        logging.getLogger("requests").setLevel(logging.WARNING)
        self.config = config

    def get_expose_details(self, expose):
        """Loads additional details for an expose by processing the expose detail URL"""
        soup = self.get_page(expose['url'])
        immo_div = soup.find("div", {"id": "divImmobilie"})
        if immo_div is not None:
            details = immo_div.find_all("div", {"class": "clear"})
            for detail in details:
                if detail.find("div", {"class": "iw_left"}) is None:
                    continue
                if detail.find("div", {"class": "iw_left"}).text.strip() == 'Die Wohnung':
                    description_element = detail.find("div", {"class": "iw_right"})
                    if description_element is None or description_element.find("p") is None:
                        continue
                    description = description_element.find("p").text
                    if re.match(r'.*sofort.*', description, re.MULTILINE|re.DOTALL|re.IGNORECASE):
                        expose['from'] = datetime.datetime.now().strftime("%2d.%2m.%Y")
                    date_string = re.match(r'.*(\d{2}.\d{2}.\d{4}).*',
                                           description, re.MULTILINE|re.DOTALL)
                    if date_string is not None:
                        expose['from'] = date_string[1]
            if 'from' not in expose:
                expose['from'] = datetime.datetime.now().strftime("%2d.%2m.%Y")
        return expose

    # pylint: disable=too-many-locals
    def extract_data(self, soup):
        """Extracts all exposes from a provided Soup object"""
        entries = list()
        soup = soup.find("main")

        try:
            title_elements = soup.find_all("h2")
        except AttributeError:
            return entries
        expose_ids = soup.find_all("a", id=True)

        for idx, title_el in enumerate(title_elements):

            try:
                price = expose_ids[idx].find(
                    "div", attrs={"data-test": "price"}).text
            except IndexError:
                self.__log__.error("Kein Preis angegeben")
                price = "Auf Anfrage"

            try:
                size = expose_ids[idx].find(
                    "div", attrs={"data-test": "area"}).text
            except IndexError:
                size = "Nicht gegeben"
                self.__log__.error("Quadratmeter nicht angegeben")

            try:
                rooms = expose_ids[idx].find(
                    "div", attrs={"data-test": "rooms"}).text
            except IndexError:
                self.__log__.error("Keine Zimmeranzahl gegeben")
                rooms = "Nicht gegeben"

            url = expose_ids[idx].get("href")

            picture = expose_ids[idx].find("picture")
            if picture is not None:
                image = picture.find("source").get("data-srcset")

            else:
                image = None

            try:
                address = expose_ids[idx].find(
                    "div", attrs={"class": re.compile("IconFact.*")})
                address = address.find("span").text
            except IndexError:
                self.__log__.error("Keine Addresse gegeben")
                address = "Nicht gegeben"

            details = {
                'id': expose_ids[idx].get("id"),
                'image': image,
                'url': url,
                'title': title_el.text.strip(),
                'rooms': rooms,
                'price': price,
                'size': size,
                'address': address,
                'crawler': self.get_name()
            }
            entries.append(details)

        self.__log__.debug('extracted: %d', entries)

        return entries
