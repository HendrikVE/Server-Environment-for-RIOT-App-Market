#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
 * Copyright (C) 2017 Hendrik van Essen
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
"""

# this script will read sql statements out of files and execute them to setup the database

from __future__ import print_function

import MySQLdb
import os

import db_config as config

CUR_DIR = os.path.abspath(os.path.dirname(__file__))

db = MySQLdb.connect(config.db_config["host"],
                     config.db_config["user_backend"],
                     config.db_config["passwd_backend"],
                     config.db_config["db"])

# cursor object to execute queries
db_cursor = db.cursor()

sql_file_list = [
    os.path.join(CUR_DIR, "sql", "modules.sql"),
    os.path.join(CUR_DIR, "sql", "boards.sql"),
    os.path.join(CUR_DIR, "sql", "applications.sql")
]

for sql_file_path in sql_file_list:

    try:
        with open(sql_file_path, "r") as sql_file:

            lines = sql_file.readlines()

            for sql_query in lines:
                db_cursor.execute(sql_query)

            db.commit()

    except Exception as e:
        print (e)

db_cursor.close()
db.close()