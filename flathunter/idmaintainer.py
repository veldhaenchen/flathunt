import threading
import sqlite3 as lite
import datetime
import sys

# ~ Logging KungFoo
import logging

__author__ = "Nody"
__version__ = "0.1"
__maintainer__ = "Nody"
__email__ = "harrymcfly@protonmail.com"
__status__ = "Prodction"

class AlreadySeenFilter:

    def __init__(self, id_watch):
        self.id_watch = id_watch
        self.processed = self.id_watch.get()

    def is_interesting(self, expose):
        if expose['id'] not in self.processed:
            self.id_watch.add(expose['id'])
            self.processed.append(expose['id'])
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
                self.threadlocal.connection.commit()
            except lite.Error as e:
                self.__log__.error("Error %s:" % e.args[0])
                raise e
        return connection

    def add(self, expose_id):
        self.__log__.debug('add(' + str(expose_id) + ')')
        cur = self.get_connection().cursor()
        cur.execute('INSERT INTO processed VALUES(' + str(expose_id) + ')')
        self.get_connection().commit()

    def get(self):
        res = []
        cur = self.get_connection().cursor()
        cur.execute("SELECT * FROM processed ORDER BY 1")
        while True:
            row = cur.fetchone()
            if row == None:
                break
            res.append(row[0])

        self.__log__.info('already processed: ' + str(len(res)))
        self.__log__.debug(str(res))
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
