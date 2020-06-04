from flathunter.web import app
from flask import render_template
from flask import jsonify
from flask_api import status
import datetime

@app.route('/index')
@app.route('/')
def index():
    hunter = app.config["HUNTER"]
    return render_template("index.html", title="Home", exposes=hunter.get_recent_exposes(), last_run=hunter.get_last_run_time())

# Accept GET requests here to support Google Cloud Cron calls
@app.route('/hunt', methods=['GET','POST'])
def hunt():
    hunter = app.config["HUNTER"]
    hunter.hunt_flats()
    return jsonify(status="Success", completedAt=str(hunter.get_last_run_time())), status.HTTP_201_CREATED
