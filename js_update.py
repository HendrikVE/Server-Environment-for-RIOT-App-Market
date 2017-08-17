#!/usr/bin/python

# script to update main.js in riotam-website/

import db_config as config
import MySQLdb
import os

def main():

	os.chdir("..")

	try:

		content_string_begin = ""
		content_string_end   = ""

		with open("riotam-website/main.js", "r") as javascript_file:

			content = javascript_file.read()

			tag_begin = "/* begin of replacement */"
			tag_end   = "/* end of replacement */"

			# setting the index to replace (keep begin and end strings for later updates!)
			index_begin = content.index(tag_begin) + len(tag_begin) + 1
			index_end   = content.index(tag_end)

			content_string_begin = content[:index_begin]
			content_string_end   = content[index_end:]

		# override old file with new content
		with open("riotam-website/main.js", "w") as javascript_file:

			javascript_file.write(content_string_begin)

			javascript_file.write(get_devices_replacement())

			javascript_file.write(content_string_end)


	except IOError, e:
		print e


def get_devices_replacement():
	
	db = MySQLdb.connect(config.db_config["host"], config.db_config["user"], config.db_config["passwd"], config.db_config["db"])

	# cursor object to execute queries
	db_cursor = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)

	db_cursor.execute("SELECT * FROM devices")
	results = db_cursor.fetchall()

	str_list = []
	for row in results:
		if row["product_id"] is not None:
			str_list.append("{{vendorId: {!s}, productId: {!s}}}, //{!s}\n".format(row["vendor_id"], row["product_id"], row["name"]))
		else:
			str_list.append("{{vendorId: {!s}}}, //{!s}\n".format(row["vendor_id"], row["name"]))

	db_cursor.close()
	db.close()
	
	return "".join(str_list)

if __name__ == "__main__":
	main()