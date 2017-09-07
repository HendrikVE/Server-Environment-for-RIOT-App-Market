#!/usr/bin/env python
import os, errno, sys, time, shutil, subprocess
from shutil import copyfile, copytree
import tempfile
import json, base64
import db_config as config
import MySQLdb

db = None
db_cursor = None

# enum-like construct
class ArgumentMode:
	Modules, Device = range(2)
	
build_result = {
	"cmd_output" : 	"",
	"device" : None,
	"application_name" : "application",
	"output_file" : None,
	"output_file_extension" : None,
	"output_archive" : None,
	"output_archive_extension" : None
}

def main(cmd):
	
	cmd = remove_unnecessary_spaces(cmd)
	
	args = cmd.split(" ")
	
	# dictionary as replacement for switch-case
	switcher = {
		"--modules": ArgumentMode.Modules,
		"--device": ArgumentMode.Device,
	}
	
	modules = []
	device = "native"
	
	current_mode  = None
	for arg in args:
		
		new_mode = switcher.get(arg, None)
		
		if current_mode is None and new_mode is None:
			build_result["cmd_output"] += "error, wrong commands"
			break
			
		elif new_mode is not None:
			current_mode = new_mode
			
		else:
			if current_mode == ArgumentMode.Modules:
				modules.append(arg)
				
			elif current_mode == ArgumentMode.Device:
				device = arg
				
	build_result["device"] = device
				
	if len(modules) == 0:
		build_result["cmd_output"] += "no module selected!"
		
	else:
		
		parent_path = "RIOT/generated_by_riotam/"
		# unique application directory name, TODO: using locks to be safe
		ticket_id = time.time()
		application_name = "application{!s}".format(ticket_id)
		application_path = application_name + "/"
		full_path = parent_path + application_path
		
		build_result["application_name"] = application_name
		
		create_directories(full_path)
		
		write_makefile(device, modules, application_name, full_path)
		
		# just for testing!
		copyfile("main.c", full_path + "main.c")
		
		execute_makefile(full_path)
		
		try:
			file_extension = "elf" # TODO: or hex
			build_result["output_file_extension"] = file_extension
			
			path_binary = full_path + "bin/" + device + "/" + application_name + "." + file_extension
			
			with open(path_binary, "rb") as output_file:
				build_result["output_file"] = base64.b64encode(output_file.read())
			"""	
			try:
				path_temporary_directory = get_temporary_directory(ticket_id)
				copytree("RIOT_stripped/", path_temporary_directory)
			
			except Exception as e:
				build_result["cmd_output"] += str(e)
			"""
			archieve_extension = "zip"
			build_result["output_archive_extension"] = archieve_extension
			
			#shutil.make_archive("RIOT_stripped", archieve_extension, "RIOT_stripped")

			with open("RIOT_stripped" + "." + archieve_extension, "rb") as output_archive:
				build_result["output_archive"] = base64.b64encode(output_archive.read())
			
			
		except Exception as e:
			build_result["cmd_output"] += path_binary + " not found"
		
		# using iframe for automatic start of download, https://stackoverflow.com/questions/14886843/automatic-download-launch
		#build_result["cmd_output"] += "<div style=""display:none;""><iframe id=""frmDld"" src=""timer_periodic_wakeup.elf""></iframe></div>"
		
		# delete temporary directory after finished build
		shutil.rmtree(full_path)
		
	print json.dumps(build_result)
	
def get_temporary_directory(ticket_id):
	
	return tempfile.gettempdir() + "/riotam/{!s}/".format(ticket_id)
	
def remove_unnecessary_spaces(string):
	
	while "  " in string:
		string = string.replace("  ", " ")
		
	return string

def init_db():
	
	global db
	db = MySQLdb.connect(config.db_config["host"], config.db_config["user"], config.db_config["passwd"], config.db_config["db"])

	# cursor object to execute queries
	global db_cursor
	db_cursor = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
	
def close_db():
	
	db_cursor.close()
	db.close()

def get_module_name(id):
	
	db_cursor.execute("SELECT name FROM modules WHERE id=%s", (id,))
	results = db_cursor.fetchall()

	if len(results) != 1:
		"error in database: len(results != 1)"
		return None
	else:
		return results[0]["name"]
	
def create_directories(path):
	
	try:
		os.makedirs(path)

	except OSError as e:

		if e.errno != errno.EEXIST:
			raise
			
def write_makefile(device, modules, application_name, path):
	
	filename = "Makefile"
	with open(path + filename, "w") as makefile:

		makefile.write("APPLICATION = " + application_name)
		makefile.write("\n\n")

		# TODO: check, if device is in database!!!
		makefile.write("BOARD ?= {!s}".format(device))
		makefile.write("\n\n")

		makefile.write("RIOTBASE ?= $(CURDIR)/../..")
		makefile.write("\n\n")

		init_db()
		
		for module in modules:
			module_name = get_module_name(module)

			if module_name is None:
				build_result["cmd_output"] += "error while reading modules from database"
				break

			else :
				makefile.write("USEMODULE += {!s}\n".format(module_name))

		makefile.write("\n")
		makefile.write("include $(RIOTBASE)/Makefile.include")
		
		close_db()
		
def execute_makefile(path):
	
	# make does preserve the path when changing via "--directory=dir"
	
	proc = subprocess.Popen(["make", "--directory={!s}".format(path)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	build_result["cmd_output"] += proc.communicate()[0].replace("\n", "<br>")
	
	return

if __name__ == "__main__":
	
	main(sys.argv[1])