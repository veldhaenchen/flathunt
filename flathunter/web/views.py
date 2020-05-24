from flathunter.web import app
from flask import render_template
from flask import jsonify
from flask_api import status

@app.route('/index')
@app.route('/')
def index():
    return render_template("index.html", title="Home")

# Accept GET requests here to support Google Cloud Cron calls
@app.route('/hunt', methods=['GET','POST'])
def hunt():
    with app.config["HUNTER"].id_watch.connect() as connection:
        app.config["HUNTER"].hunt_flats(connection)
        return jsonify(status="Success"), status.HTTP_201_CREATED
