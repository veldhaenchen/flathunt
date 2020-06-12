import threading
import sqlite3 as lite
import datetime
import sys
import json
import logging

from flathunter.abstract_processor import Processor

__author__ = "Nody"
__version__ = "0.1"
__maintainer__ = "Nody"
__email__ = "harrymcfly@protonmail.com"
__status__ = "Prodction"

class SaveAllExposesProcessor(Processor):

    def __init__(self, config, id_watch):
        self.id_watch = id_watch

    def process_expose(self, expose):
        self.id_watch.save_expose(expose)
        return expose

class AlreadySeenFilter:

    def __init__(self, id_watch):
        self.id_watch = id_watch

    def is_interesting(self, expose):
        if not self.id_watch.is_processed(expose['id']):
            self.id_watch.mark_processed(expose['id'])
            return True
        return False

class IdMaintainer:
    __log__ = logging.getLogger(__name__)

    def __init__(self, db_name):
        self.db_name = db_name
        self.threadlocal = threading.local()

    def get_connection(self):
        connection = getattr(self.threadlocal, 'connection', None)
        if connection is None:
            try:
                self.threadlocal.connection = lite.connect(self.db_name)
                connection = self.threadlocal.connection
                cur = self.threadlocal.connection.cursor()
                cur.execute('CREATE TABLE IF NOT EXISTS processed (ID INTEGER)')
                cur.execute('CREATE TABLE IF NOT EXISTS executions (timestamp timestamp)')
                cur.execute('CREATE TABLE IF NOT EXISTS exposes (id INTEGER, created TIMESTAMP, crawler STRING, details BLOB, PRIMARY KEY (id, crawler))')
                cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, settings BLOB)')
                self.threadlocal.connection.commit()
            except lite.Error as e:
                self.__log__.error("Error %s:" % e.args[0])
                raise e
        return connection

    def is_processed(self, expose_id):
        self.__log__.debug('is_processed(' + str(expose_id) + ')')
        cur = self.get_connection().cursor()
        cur.execute('SELECT id FROM processed WHERE id = ?', (expose_id,))
        row = cur.fetchone()
        return (row is not None)

    def mark_processed(self, expose_id):
        self.__log__.debug('mark_processed(' + str(expose_id) + ')')
        cur = self.get_connection().cursor()
        cur.execute('INSERT INTO processed VALUES(' + str(expose_id) + ')')
        self.get_connection().commit()

    def save_expose(self, expose):
        cur = self.get_connection().cursor()
        cur.execute('INSERT OR REPLACE INTO exposes(id, created, crawler, details) VALUES (?, ?, ?, ?)', (int(expose['id']), datetime.datetime.now(), expose['crawler'], json.dumps(expose)))
        self.get_connection().commit()

    def get_exposes_since(self, min_datetime):
        def row_to_expose(row):
            obj = json.loads(row[2])
            obj['created_at'] = row[0]
            return obj
        cur = self.get_connection().cursor()
        cur.execute('SELECT created, crawler, details FROM exposes WHERE created >= ? ORDER BY created DESC', (min_datetime,))
        return list(map(lambda t: row_to_expose(t), cur.fetchall()))

    def get_recent_exposes(self, count, filter=None):
        cur = self.get_connection().cursor()
        cur.execute('SELECT details FROM exposes ORDER BY created DESC')
        res = []
        next = []
        while (len(res) < count):
            if len(next) == 0:
                next = cur.fetchmany()
                if len(next) == 0:
                    break
            expose = json.loads(next.pop()[0])
            if filter is None or filter.is_interesting_expose(expose):
                res.append(expose)
        return res

    def save_settings_for_user(self, user_id, settings):
        cur = self.get_connection().cursor()
        cur.execute('INSERT OR REPLACE INTO users VALUES (?, ?)', (user_id, json.dumps(settings)))
        self.get_connection().commit()

    def get_settings_for_user(self, user_id):
        cur = self.get_connection().cursor()
        cur.execute('SELECT settings FROM users WHERE id = ?', (user_id,))
        row = cur.fetchone()
        if row == None:
            return None
        return json.loads(row[0])

    def get_user_settings(self):
        cur = self.get_connection().cursor()
        cur.execute('SELECT id, settings FROM users')
        res = []
        for row in cur.fetchall():
            res.append((row[0], json.loads(row[1])))
        return res

    def get_last_run_time(self):
        cur = self.get_connection().cursor()
        cur.execute("SELECT * FROM executions ORDER BY timestamp DESC LIMIT 1")
        row = cur.fetchone()
        if row == None:
            return None
        return datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')

    def update_last_run_time(self):
        cur = self.get_connection().cursor()
        result = datetime.datetime.now()
        cur.execute('INSERT INTO executions VALUES(?);', (result,))
        self.get_connection().commit()
        return result
