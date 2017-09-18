#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import MySQLdb

import config.db_config as config


class MyDatabase(object):

    _db_connection = None
    _db_cursor = None

    def __init__(self):
        self._db_connection = MySQLdb.connect(config.db_config["host"],
                                              config.db_config["user"],
                                              config.db_config["passwd"],
                                              config.db_config["db"])

        self._db_cursor = self._db_connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    def query(self, query, params = ""):
        return self._db_cursor.execute(query, params)

    def fetchall(self):
        return self._db_cursor.fetchall()

    def __del__(self):
        self._db_cursor.close()
        self._db_connection.close()
