#!/usr/bin/python

import db_config as config
import MySQLdb
import os

db_cursor = None
db = None

def main():
	
	global db_cursor, db
	
	db = MySQLdb.connect(config.db_config["host"], config.db_config["user"], config.db_config["passwd"], config.db_config["db"])

	# cursor object to execute queries
	db_cursor = db.cursor()

	update_modules()
	update_devices()

	db_cursor.close()
	db.close()
	
def update_modules():
	
	db_cursor.execute("TRUNCATE modules")
	
	for i in range(len(config.module_directories)):

		module_directory = config.module_directories[i]
		path = config.path_root + module_directory + "/"

		for item in os.listdir(path):
			if not os.path.isfile(os.path.join(path, item)):

				# ignoring include directories
				if item == "include":
					continue

				description = get_description(path + item + "/doc.txt")
				
				sql = "INSERT INTO modules (name, path, description, group_identifier) VALUES (%s, %s, %s, %s);"
				db_cursor.execute(sql, (item, path + item + "/", description, module_directory))

	db.commit()
	
def update_devices():
	
	db_cursor.execute("TRUNCATE devices")
	
	path = config.path_root + "boards/"

	for item in os.listdir(path):
		if not os.path.isfile(os.path.join(path, item)):
			
			sql = "INSERT INTO devices (display_name, internal_name, flash_program) VALUES (%s, %s, %s);"
			db_cursor.execute(sql, (item, item, "openocd"))
			
	db.commit()

def get_description(path):
	
	description = ""
	
	try:
		with open(path) as file:
			for line in file:
				if "@brief" in line:
					index = line.find("@brief") + len("@brief")
					description = line[index:].strip()
					break
					
				
	except IOError:
		# ignore missing doc.txt
		return None
		
	if description == "":
		description = None
		
	return description  

if __name__ == "__main__":
	main()