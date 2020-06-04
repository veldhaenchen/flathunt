##
# Startup file for Google Cloud deployment
##
import os

from flathunter.idmaintainer import IdMaintainer
from flathunter.googlecloud_idmaintainer import GoogleCloudIdMaintainer
from flathunter.hunter import Hunter
from flathunter.config import Config

from flathunter.web import app

if __name__ == '__main__':
    # Use the SQLite DB file if we are running locally
    id_watch = IdMaintainer('%s/processed_ids.db' % os.path.dirname(os.path.abspath(__file__)))
else:
    # Use Google Cloud DB if we run on the cloud
    id_watch = GoogleCloudIdMaintainer()

hunter = Hunter(Config(), id_watch)

app.config["HUNTER"] = hunter

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
