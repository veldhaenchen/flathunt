import sqlite3 as lite
import sys

# ~ Logging KungFoo
import logging

__author__ = "Nody"
__version__ = "0.1"
__maintainer__ = "Nody"
__email__ = "harrymcfly@protonmail.com"
__status__ = "Prodction"


class IdMaintainer:
    __log__ = logging.getLogger(__name__)

    def __init__(self, db_name):
        self.db_name = db_name
        self.default_connection = None
        try:
            self.default_connection = self.connect()
            cur = self.default_connection.cursor()
            cur.execute('CREATE TABLE IF NOT EXISTS processed (ID INTEGER)')
            self.default_connection.commit()

        except lite.Error as e:
            self.__log__.error("Error %s:" % e.args[0])
            sys.exit(1)

    def connect(self):
        return lite.connect(self.db_name)

    def add(self, expose_id, connection=None):
        self.__log__.debug('add(' + str(expose_id) + ')')
        if connection is None:
            connection = self.default_connection
        cur = connection.cursor()
        cur.execute('INSERT INTO processed VALUES(' + str(expose_id) + ')')
        connection.commit()

    def get(self, connection=None):
        if connection is None:
            connection = self.default_connection
        res = []
        cur = connection.cursor()
        cur.execute("SELECT * FROM processed ORDER BY 1")
        while True:
            row = cur.fetchone()
            if row == None:
                break
            res.append(row[0])

        self.__log__.info('already processed: ' + str(len(res)))
        self.__log__.debug(str(res))
        return res
