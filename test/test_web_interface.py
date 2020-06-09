import pytest
import tempfile
import yaml
import json
import requests_mock

from flask import session

from flathunter.web import app
from flathunter.web_hunter import WebHunter
from flathunter.idmaintainer import IdMaintainer
from flathunter.config import Config

from dummy_crawler import DummyCrawler

DUMMY_CONFIG = """
telegram:
  bot_token: 1234xxx.12345

message: "{title}"

urls:
  - https://www.example.com/liste/berlin/wohnungen/mieten?roomi=2&prima=1500&wflmi=70&sort=createdate%2Bdesc
    """

@pytest.fixture
def hunt_client():
    app.config['TESTING'] = True
    with tempfile.NamedTemporaryFile(mode='w+') as temp_db:
        config = Config(string=DUMMY_CONFIG)
        config.set_searchers([DummyCrawler()])
        app.config['HUNTER'] = WebHunter(config, IdMaintainer(temp_db.name))
        app.config['BOT_TOKEN'] = "1234xxx.12345"
        app.secret_key = b'test_session_key'

        with app.test_client() as hunt_client:
            yield hunt_client

def test_get_index(hunt_client):
    rv = hunt_client.get('/')
    assert b'<h1>Flathunter</h1>' in rv.data

def test_get_index_with_exposes(hunt_client):
    app.config['HUNTER'].hunt_flats()
    rv = hunt_client.get('/')
    assert b'<div class="expose">' in rv.data

@requests_mock.Mocker(kw='m')
def test_hunt_with_users(hunt_client, **kwargs):
    m = kwargs['m']
    mock_response = '{"ok":true,"result":{"message_id":456,"from":{"id":1,"is_bot":true,"first_name":"Wohnbot","username":"wohnung_search_bot"},"chat":{"id":5,"first_name":"Arthur","last_name":"Taylor","type":"private"},"date":1589813130,"text":"hello arthur"}}'
    for title in [ 'wg', 'ruhig', 'gruen', 'tausch', 'flat' ]:
        m.get('https://api.telegram.org/bot1234xxx.12345/sendMessage?chat_id=1234&text=Great+flat+' + title + '+terrible+landlord', text=mock_response)
    app.config['HUNTER'].set_filters_for_user(1234, {})
    assert app.config['HUNTER'].get_filters_for_user(1234) == {}
    app.config['HUNTER'].hunt_flats()
    rv = hunt_client.get('/')
    assert b'<div class="expose">' in rv.data

def test_login_with_telegram(hunt_client):
    rv = hunt_client.get('/login_with_telegram?id=1234&first_name=Jason&last_name=Bourne&username=mattdamon&photo_url=https%3A%2F%2Fi.example.com%2Fprofile.jpg&auth_date=123455678&hash=c691a55de4e28b341ccd0b793d4ca17f09f6c87b28f8a893621df81475c25952')
    assert rv.status_code == 302
    assert rv.headers['location'] == 'http://localhost/'
    assert 'user' in session
    assert session['user']['first_name'] == 'Jason'
    assert json.dumps(session['user']) == '{"id": "1234", "first_name": "Jason", "last_name": "Bourne", "username": "mattdamon", "photo_url": "https://i.example.com/profile.jpg", "auth_date": "123455678"}'

def test_login_with_invalid_url(hunt_client):
    rv = hunt_client.get('/login_with_telegram?username=mattdamon&id=1234&first_name=Jason&last_name=Bourne&photo_url=https%3A%2F%2Fi.example.com%2Fprofile.jpg&auth_date=123455678')
    assert rv.status_code == 302
    assert rv.headers['location'] == 'http://localhost/'
    assert 'user' in session
    assert session['user'] is None