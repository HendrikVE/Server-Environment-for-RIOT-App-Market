#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# this script will read sql statements out of files and execute them to setup the database

import db_config as config
import MySQLdb

db = MySQLdb.connect(config.db_config["host"], config.db_config["user"], config.db_config["passwd"], config.db_config["db"])

# cursor object to execute queries
db_cursor = db.cursor()

sql_file_list = [
    "database/modules.sql",
    "database/boards.sql",
    "database/applications.sql"
]

for sql_file_path in sql_file_list:
	
    try:
        with open(sql_file_path, "r") as sql_file:

            lines = sql_file.readlines()

            for sql_query in lines:
                db_cursor.execute(sql_query)

            db.commit()

    except Exception as e:
        print e

db_cursor.close()
db.close()