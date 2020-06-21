import collections
import hmac
import hashlib
import datetime
import re
from urllib import parse

from flathunter.web import app
from flathunter.web.util import sanitize_float
from flathunter.filter import FilterBuilder
from flask import render_template, jsonify, request, session, redirect
from flask_api import status
from json import JSONEncoder

class AuthenticationError(Exception):
    pass

class User(dict):

    def __init__(self, parameters):
        super().__init__(parameters)
        for field in [ 'id' ]:
            if field not in parameters:
                raise AuthenticationError("Missing field: " + field)

def auth_hash(params, token):
    secret = hashlib.sha256()
    secret.update(token.encode('utf-8'))
    sorted_params = collections.OrderedDict(sorted(params.items()))
    msg = "\n".join(["{}={}".format(k, v) for k, v in sorted_params.items()])
    return hmac.new(secret.digest(), msg.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()

def sign_hash(params, token):
    params['hash'] = auth_hash(params, token)
    return params

def user_for_params(params):
    if 'hash' not in params:
        app.logger.warning("Got login request with no authentication hash")
        return None
    params_hash = params.pop('hash')
    calculated_hash = auth_hash(params, app.config['BOT_TOKEN'])

    if params_hash == calculated_hash:
        return User(params)
    app.logger.warning("Unable to authenticate user: " + str(params) + " (exp: " + calculated_hash + ")")
    return None

def generate_dummy_login_url():
    return '/login_with_telegram?' + parse.urlencode(sign_hash(
        {
            'username': 'mattdamon',
            'id': 1234,
            'first_name': 'Jason',
            'last_name': 'Bourne',
            'photo_url': 'https://i.example.com/profile.jpg',
            'auth_date': 123455678
        }, app.config['BOT_TOKEN']))

def filter_values_for_user():
    if 'user' not in session:
        return None
    return app.config["HUNTER"].get_filters_for_user(session['user']['id'])

def filter_for_user():
    if filter_values_for_user() is None:
        return None
    return FilterBuilder().read_config({ 'filters': filter_values_for_user() }).build()

def form_filter_values():
    values = {}
    filters = filter_values_for_user()
    if filters is not None:
        for field in [ 'max_price', 'min_price', 'max_size', 'min_size', 'max_rooms', 'min_rooms' ]:
            values[field] = int(filters[field]) if field in filters else ""
    return values

def notifications_muted_for_user():
    if 'user' not in session:
        return None
    return app.config["HUNTER"].notifications_muted_for_user(session['user']['id'])

@app.route('/index')
@app.route('/')
def index():
    hunter = app.config["HUNTER"]
    bot_name = app.config.get("BOT_NAME", None)
    domain = app.config.get("DOMAIN", None)
    filter_set = filter_for_user()
    form_values = form_filter_values()
    return render_template("index.html",
        title="Home", exposes=hunter.get_recent_exposes(filter_set=filter_set), last_run=hunter.get_last_run_time(),
        bot_name=bot_name, domain=domain,
        login_url=generate_dummy_login_url(),
        filters=form_values, notifications_enabled=(not notifications_muted_for_user()))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

# Accept GET requests here to support Google Cloud Cron calls
@app.route('/hunt', methods=['GET','POST'])
def hunt():
    hunter = app.config["HUNTER"]
    hunter.hunt_flats()
    return jsonify(status="Success", completedAt=str(hunter.get_last_run_time()), body=render_template("exposes.html", exposes=hunter.get_recent_exposes())), status.HTTP_201_CREATED

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/')

@app.route('/login_with_telegram')
def login_with_telegram():
    try:
        user = user_for_params(request.args.copy())
        if user is not None:
            session['user'] = user
            app.logger.info("User is: " + str(session['user']))
        return redirect('/')
    except AuthenticationError as e:
        app.logger.error('Invalid login attempt', request.args)
        return redirect('/')

@app.route('/toggle_notifications', methods=['POST'])
def toggle_notifications():
    if 'user' not in session:
        return jsonify(status="Not found", message="Not logged in"), status.HTTP_404_NOT_FOUND
    notifications_enabled = app.config["HUNTER"].toggle_notification_status(session['user']['id'])
    app.logger.info("Notifications enabled for user toggled to: " + str(notifications_enabled))
    return jsonify(status="Updated", notifications_enabled=notifications_enabled), status.HTTP_201_CREATED

@app.route('/filter', methods=['POST'])
def update_filter():
    if 'user' not in session:
        return redirect('/')
    filters = { k: sanitize_float(v) for k,v in request.form.items() if v != "" and sanitize_float(v) is not None}
    app.config["HUNTER"].set_filters_for_user(session['user']['id'], filters)
    app.logger.info("Updated filter to: " + str(filters))
    return redirect('/')
