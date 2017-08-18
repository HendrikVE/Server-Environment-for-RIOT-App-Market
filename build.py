import sys

class ArgumentMode:
	Modules, Device = range(2)

def main(cmd):
	
	cmd = remove_unnecessary_spaces(cmd)
	
	args = cmd.split(" ")
	
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
				
		
	
def remove_unnecessary_spaces(string):
	
	while "  " in string:
		string = string.replace("  ", " ")
		
	return string

if __name__ == "__main__":
	main(sys.argv[1])