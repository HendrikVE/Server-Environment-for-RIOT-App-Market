#!/usr/bin/python
import MySQLdb

db = MySQLdb.connect(host   = "localhost",
                     user   = "hendrik",
                     passwd = "4EYXR21m",
                     db     = "riot_devices")

# you must create a Cursor object. It will let
#  you execute all the queries you need
dbCursor = db.cursor()

# Use all the SQL you like
dbCursor.execute("SELECT * FROM devices")

# print all the first cell of all the rows
for row in dbCursor.fetchall():
	for data in row:
		print data

db.close()