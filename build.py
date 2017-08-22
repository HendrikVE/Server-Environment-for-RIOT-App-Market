import sys
import os
import db_config as config
import MySQLdb

# enum-like construct
class ArgumentMode:
	Modules, Device = range(2)

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
			print "error, wrong commands"
			break
			
		elif new_mode is not None:
			current_mode = new_mode
			
		else:
			if current_mode == ArgumentMode.Modules:
				modules.append(arg)
				
			elif current_mode == ArgumentMode.Device:
				device = arg
				
	if len(modules) == 0:
		print "no module selected!"
		
	else:
		filename = "Makefile.tmp"
		with open(filename, "w") as makefile:
			
			for module in modules:
				module_name = get_module_name(module)
				
				if module_name is None:
					print "error while reading modules from database"
					break
					
				else :
					makefile.write("USEMODULE += {!s}\n".format(module_name))
					
		#os.remove(filename)
	
def remove_unnecessary_spaces(string):
	
	while "  " in string:
		string = string.replace("  ", " ")
		
	return string

def get_module_name(id):
	
	db = MySQLdb.connect(config.db_config["host"], config.db_config["user"], config.db_config["passwd"], config.db_config["db"])

	# cursor object to execute queries
	db_cursor = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)

	db_cursor.execute("SELECT name FROM modules WHERE id=%s", (id,))
	results = db_cursor.fetchall()

	db_cursor.close()
	db.close()
	
	if len(results) != 1:
		"error in database: len(results != 1)"
		return None
	else:
		return results[0]["name"]

if __name__ == "__main__":
	main(sys.argv[1])