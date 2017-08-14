#!/usr/bin/python
import db_update_config as config
import MySQLdb
import os

db = MySQLdb.connect(config.db_config["host"], config.db_config["user"], config.db_config["passwd"], config.db_config["db"])

# cursor object to execute queries
db_cursor = db.cursor()

for i in range(len(config.module_directories)):
	for (dirpath, dirnames, filenames) in os.walk(config.path_root + config.module_directories[i]):
		for dirname in dirnames:
			#db_cursor.execute()
			print "INSERT INTO modules (name, path, description) VALUES ('{!s}', '{!s}', '{!s}');".format(dirname, dirpath + dirname, " ")

for row in db_cursor.fetchall():
	for data in row:
		print data

db_cursor.close()
db.close()