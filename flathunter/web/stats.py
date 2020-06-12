import datetime
import json
from flask import render_template, jsonify, request, session, redirect
from flask_api import status

from flathunter.web import app
from flathunter.web.util import sanitize_float

@app.route('/stats')
def stats_view():
    hunter = app.config["HUNTER"]
    exposes = json.dumps(
        list(
            map(lambda e: { 'price': sanitize_float(e['price']), 'size': sanitize_float(e['size']), 'created_at': str(e['created_at']) },
                hunter.get_exposes_since(datetime.datetime.now() - datetime.timedelta(days=28)))))
    return render_template("statistics.html", title="Statistics", exposes=exposes)