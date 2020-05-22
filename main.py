##
# Startup file for Google Cloud deployment
##
import os
import yaml

from flathunter.crawl_ebaykleinanzeigen import CrawlEbayKleinanzeigen
from flathunter.crawl_immobilienscout import CrawlImmobilienscout
from flathunter.crawl_wggesucht import CrawlWgGesucht
from flathunter.crawl_immowelt import CrawlImmowelt
from flathunter.idmaintainer import IdMaintainer
from flathunter.hunter import Hunter

from flathunter.web import app

if __name__ == '__main__':
    # This is only used when running locally
    with open(r'config.yaml') as file:
        config = yaml.safe_load(file)

    searchers = [CrawlImmobilienscout(), CrawlWgGesucht(), CrawlEbayKleinanzeigen(), CrawlImmowelt()]
    id_watch = IdMaintainer('%s/processed_ids.db' % os.path.dirname(os.path.abspath(__file__)))

    hunter = Hunter(config, searchers, id_watch)

    app.config["HUNTER"] = hunter
    app.run(host='127.0.0.1', port=8080, debug=True)
