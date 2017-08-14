#!/usr/bin/python

import db_config as config
import MySQLdb

db = MySQLdb.connect(config.db_config["host"], config.db_config["user"], config.db_config["passwd"], config.db_config["db"])

# cursor object to execute queries
db_cursor = db.cursor()

with open('schema/modules.sql', 'r') as modules_schema:
	
	lines = modules_schema.readlines()
	
	for sql_query in lines:
		db_cursor.execute(sql_query)
	
db.commit()

db_cursor.close()
db.close()