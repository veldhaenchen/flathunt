# Python Flathunter-Helper

## Setup

### Virtual Environment (Optional)
To keep you python environment and site-packages clean, it is recommended
to run the project in a virtual environment. Install ```virtualenv```,
create a venv and activate.
```
$ pip install virtualenv
$ virtualenv -p /usr/bin/python3.6 venv
$ source venv/bin/activate
```


### Requirements
Install requirements from ```requirements.txt``` to run execute flathunter properly.
```
pip install -r requirements.txt
```

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

### Configuration

#### Links

Currently, ebay-kleinanzeigen and immowelt only crawl the first page, so make sure to **sort by newest offers**.

#### Bot registration
A new bot can registered with the telegram chat with the [BotFather](https://telegram.me/BotFather).

#### Chat-Ids
To get the chat id (receiver ID), the [REST-Api](https://core.telegram.org/bots/api) of telegram can be used to fetch the received messages of the Bot.
```
$ curl https://api.telegram.org/bot[BOT-TOKEN]/getUpdates
```

#### Google API
To use the distance calculation feature a [Google API-Key](https://developers.google.com/maps/documentation/javascript/get-api-key) is needed and requires the Distance Matrix API to be enabled. (This is NOT free)
Since this feature is not free, it is "disabled". Read line 62 in hunter.py to re-enable it.


## Contributers
- [@NodyHub](https://github.com/NodyHub)
- Bene
- [@tschuehly](https://github.com/tschuehly)
- [@Cugu](https://github.com/Cugu)
- [@GerRudi](https://github.com/GerRudi)
- [@xMordax](https://github.com/xMordax)


