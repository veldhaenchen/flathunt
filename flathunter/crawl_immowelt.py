import logging
import requests
import re
import datetime
from bs4 import BeautifulSoup

from flathunter.abstract_crawler import Crawler

class CrawlImmowelt(Crawler):
    __log__ = logging.getLogger(__name__)
    URL_PATTERN = re.compile(r'https://www\.immowelt\.de')

    def __init__(self):
        logging.getLogger("requests").setLevel(logging.WARNING)

    def get_results(self, search_url, max_pages=None):
        self.__log__.debug("Got search URL %s" % search_url)

        soup = self.get_page(search_url)

        # get data from first page
        entries = self.extract_data(soup)
        self.__log__.debug('Number of found entries: ' + str(len(entries)))

        return entries

    def get_page(self, search_url):
        resp = requests.get(search_url)  # TODO add page_no in url
        if resp.status_code != 200:
            self.__log__.error("Got response (%i): %s" % (resp.status_code, resp.content))
        return BeautifulSoup(resp.content, 'html.parser')

    def get_expose_details(self, expose):
        soup = self.get_page(expose['url'])
        immo_div = soup.find("div", { "id": "divImmobilie" })
        if immo_div is not None:
            details = immo_div.find_all("div", { "class": "clear" })
            for detail in details:
                if detail.find("div", { "class": "iw_left" }) is None:
                    continue
                if detail.find("div", { "class": "iw_left" }).text.strip() == 'Die Wohnung':
                    description_element = detail.find("div", { "class": "iw_right" })
                    if description_element is None or description_element.find("p") is None:
                        continue
                    description = description_element.find("p").text
                    if re.match(r'.*sofort.*', description, re.MULTILINE|re.DOTALL|re.IGNORECASE):
                        expose['from'] = datetime.datetime.now().strftime("%2d.%2d.%Y")
                    date_string = re.match(r'.*(\d{2}.\d{2}.\d{4}).*', description, re.MULTILINE|re.DOTALL)
                    if date_string is not None:
                        expose['from'] = date_string[1]
            if 'from' not in expose:
                expose['from'] = datetime.datetime.now().strftime("%2d.%2d.%Y")
        return expose

    def extract_data(self, soup):
        entries = list()
        soup = soup.find(id="listItemWrapperFixed")
        try:
            title_elements = soup.find_all("h2")
        except AttributeError:
            return entries
        expose_ids = soup.find_all("div", class_="listitem_wrap")

        # soup.find_all(lambda e: e.has_attr('data-adid'))
        # print(expose_ids)
        for idx, title_el in enumerate(title_elements):

            tags = expose_ids[idx].find_all(class_="hardfact")
            url = "https://www.immowelt.de" + expose_ids[idx].find("a").get("href")
            picture = expose_ids[idx].find("picture")
            if picture is not None:
                image = picture.find("img")['src']
            else:
                image = None
            address = expose_ids[idx].find(class_="listlocation")
            address.find("span").extract()
            address = address.text.strip()

            try:
                price = tags[0].find("strong").text.strip()
            except IndexError:
                self.__log__.error("Kein Preis angegeben")
                price = "Auf Anfrage"

            try:
                tags[1].find("div").extract()
                size = tags[1].text.strip()
            except IndexError:
                size = "Nicht gegeben"
                self.__log__.error("Quadratmeter nicht angegeben")

            try:
                tags[2].find("div").extract()
                rooms = tags[2].text.strip()
            except IndexError:
                self.__log__.error("Keine Zimmeranzahl gegeben")
                rooms = "Nicht gegeben"

            details = {
                'id': int(expose_ids[idx].get("data-estateid")),
                'image': image,
                'url': url,
                'title': title_el.text.strip(),
                'price': price,
                'size': size,
                'rooms': rooms,
                'address': address,
                'crawler': self.get_name()
            }
            entries.append(details)

        self.__log__.debug('extracted: ' + str(entries))

        return entries

    @staticmethod
    def load_address(url):
        # extract address from expose itself
        expose_html = requests.get(url).content
        expose_soup = BeautifulSoup(expose_html, 'html.parser')
        try:
            street_raw = expose_soup.find(id="street-address").text
        except AttributeError:
            street_raw = ""
        try:
            address_raw = expose_soup.find(id="viewad-locality").text
        except AttributeError:
            address_raw = ""
        address = address_raw.strip().replace("\n", "") + " " + street_raw.strip()

        return address
