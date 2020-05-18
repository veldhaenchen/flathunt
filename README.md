# Flathunter

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

A Telegram bot to help people with their flat search

## Description

Flathunter is a Python application with periodically [scrapes](https://en.wikipedia.org/wiki/Web_scraping) property listings sites that the user has configured to find new apartment listings, and sends notifications of the new apartment to the user via [Telegram](https://en.wikipedia.org/wiki/Telegram_%28software%29).

## Background

There are at least four different rental property marketplace sites that are widely used in Germany - [ImmoScout24](https://www.immobilienscout24.de/), [immowelt](https://www.immowelt.de/), [WG-Gesucht](https://www.wg-gesucht.de/) and [ebay Kleinanzeigen](https://www.wg-gesucht.de/). Most people end up searching through listings on all four sites on an almost daily basis during their flat search.

With Flathunter, instead of visiting the same pages on the same four sites every day, you can set the system up to scan every site, filtering by your search criteria, and notify you when new flats become available that meet your criteria.

## Install

Flathunter is a Python3 project - you will need Python3 installed to run the code. We recommend using [pipenv](https://pipenv-fork.readthedocs.io/en/latest/) to setup and configure your project. Install `pipenv` according to the instructions on the `pipenv` site, then run:

```sh
$ pipenv install
```

from the project directory to install the dependencies. Once the dependencies are installed, and every time you come back to the project in a new shell, run:

```sh
$ pipenv shell
```

to launch a Python environment with the dependencies that your project requires.

### Configuration

Before running the project for the first time, copy `config.yaml.dist` to `config.yaml`. The `urls` and `telegram` sections of the config file must be configured according to your requirements before the project will run. 

#### URLs

 * Currently, ebay-kleinanzeigen and immowelt only crawl the first page, so make sure to **sort by newest offers**.
 * Your links should point to the German version of the websites, since it is tested only there. Otherwise you might have problems.

#### Telegram

To be able to send messages to you over Telegram, you need to register a new bot with the [BotFather](https://telegram.me/BotFather) for `flathunter` to use. Through this process, a "Bot Token" will be created for you, which should be configured under `bot_token` in the config file.

To know who should Telegram messages should be sent to, the "Chat IDs" of the recipients must be added to the config file under `receiver_ids`. To work out your own Chat ID, send a message to your new bot, then run:


```
$ curl https://api.telegram.org/bot[BOT-TOKEN]/getUpdates
```

to get list of messages the Bot has received. You will see your Chat ID in there.

#### Google API

To use the distance calculation feature a [Google API-Key](https://developers.google.com/maps/documentation/javascript/get-api-key) is needed and requires the Distance Matrix API to be enabled. (This is NOT free)

Since this feature is not free, it is "disabled". Read line 62 in hunter.py to re-enable it.

## Usage
```
usage: flathunter.py [-h] [--config CONFIG]

Searches for flats on Immobilienscout24.de and wg-gesucht.de and sends results
to Telegram User

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Config file to use. If not set, try to use
                        '~git-clone-dir/config.yaml'

```

## Testing

The `unittest`-based test suite can be run with:

```sh
$ python -m unittest discover -s test
```

from the project root.

## Contributers
- [@NodyHub](https://github.com/NodyHub)
- Bene
- [@tschuehly](https://github.com/tschuehly)
- [@Cugu](https://github.com/Cugu)
- [@GerRudi](https://github.com/GerRudi)
- [@xMordax](https://github.com/xMordax)
- [@codders](https://github.com/codders)
