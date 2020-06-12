from flask import Flask

app = Flask(__name__)

import flathunter.web.views
import flathunter.web.stats
