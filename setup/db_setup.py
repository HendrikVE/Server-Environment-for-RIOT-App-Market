#!/usr/bin/python

# this script will read sql statements out of files and execute them to setup the database

import db_config as config
import MySQLdb

db = MySQLdb.connect(config.db_config["host"], config.db_config["user"], config.db_config["passwd"], config.db_config["db"])

# cursor object to execute queries
db_cursor = db.cursor()

try:
	with open('database/modules.sql', 'r') as modules_sql:
	
		lines = modules_sql.readlines()

		for sql_query in lines:
			db_cursor.execute(sql_query)

		db.commit()
	
except Exception, e:
	print e

try:
	with open('database/devices.sql', 'r') as modules_sql:

		lines = modules_sql.readlines()

		for sql_query in lines:
			db_cursor.execute(sql_query)

		db.commit()

except Exception, e:
	print e

db_cursor.close()
db.close()