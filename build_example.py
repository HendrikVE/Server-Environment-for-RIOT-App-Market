#!/usr/bin/env python
import os, errno, sys, time, subprocess
from shutil import copyfile, copytree, rmtree
import json, base64
import config.db_config as config
import MySQLdb
import logging
import tarfile
import glob

db = None
db_cursor = None

# enum-like construct
class ArgumentMode:
    Applications, Device = range(2)
    
build_result = {
    "cmd_output" :     "",
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
        "--application": ArgumentMode.Applications,
        "--device": ArgumentMode.Device,
    }
    
    applicationID = None
    device = None
    
    current_mode  = None
    for arg in args:
        
        new_mode = switcher.get(arg, None)
        
        if current_mode is None and new_mode is None:
            build_result["cmd_output"] += "error, wrong commands"
            break
            
        elif new_mode is not None:
            current_mode = new_mode
            
        else:
            if current_mode == ArgumentMode.Applications:
                applicationID = arg
                
            elif current_mode == ArgumentMode.Device:
                device = arg
                
    if applicationID is None:
        build_result["cmd_output"] += "no module selected!"
        
    elif device is None:
        build_result["cmd_output"] += "no device specified!"
        
    else:
        
        build_result["device"] = device
        
        parent_path = "RIOT/generated_by_riotam/"
        # unique application directory name, TODO: using locks to be safe
        ticket_id = time.time()
        application_name = "application{!s}".format(ticket_id)
        application_path = application_name + "/"
        full_path = parent_path + application_path
        
        temporary_directory = get_temporary_directory(ticket_id)
        
        build_result["application_name"] = application_name
        
        application_display_name = get_application_name(applicationID)
        copytree("RIOT/examples/" + application_display_name + "/", full_path)
        
        replace_application_name(full_path + "Makefile", application_name, device)
        
        execute_makefile(full_path, device)
        
        try:
            """ IMAGE FILE """
            file_extension = "elf" # TODO: or hex
            build_result["output_file_extension"] = file_extension
            
            binary_path = full_path + "bin/" + device + "/" + application_name + "." + file_extension
            build_result["output_file"] = file_as_base64(binary_path)
            
            
            
            """ ARCHIVE FILE """
            archieve_extension = "tar"
            build_result["output_archive_extension"] = archieve_extension
            
            # [(src_path, dest_path)]
            binary_dest_path = binary_path.replace("RIOT/", "RIOT_stripped/")
            makefile_dest_path = full_path.replace("RIOT/", "RIOT_stripped/")
            
            single_copy_operations = [
                (binary_path, binary_dest_path),
                (full_path + "Makefile", makefile_dest_path + "Makefile")
            ]
            
            stripped_repo_path = prepare_stripped_repo("RIOT_stripped/", temporary_directory, single_copy_operations, device)
            archive_path = zip_repo(stripped_repo_path, temporary_directory + "RIOT_stripped.tar")
            
            build_result["output_archive"] = file_as_base64(archive_path)
            
        except Exception as e:
            build_result["cmd_output"] += "something went wrong on server side"
        
        # using iframe for automatic start of download, https://stackoverflow.com/questions/14886843/automatic-download-launch
        #build_result["cmd_output"] += "<div style=""display:none;""><iframe id=""frmDld"" src=""timer_periodic_wakeup.elf""></iframe></div>"
        
        # delete temporary directories after finished build
        #rmtree(full_path)
        #rmtree(temporary_directory)
        
    print json.dumps(build_result)
    
def replace_application_name(path, application_name, device):
    
    file_content = []
    with open(path, "r") as makefile:

        lines = makefile.readlines()

        for line in lines:
            file_content.append(line)

    with open(path, "w") as makefile:
        for line in file_content:

            if "APPLICATION" in line:
                makefile.write("APPLICATION = {!s}\n".format(application_name))
                
            elif "BOARD" in line:
                makefile.write("BOARD = {!s}\n".format(device))
                
            else:
                makefile.write(line)
    
def prepare_stripped_repo(src_path, temporary_directory, single_copy_operations, device):
    
    try:
        dest_path = temporary_directory + "RIOT_stripped/"
        copytree(src_path, dest_path)
        
        try:
            # remove all unnecessary boards
            path_boards = dest_path + "boards/"
            for item in os.listdir(path_boards):
                if not os.path.isfile(os.path.join(path_boards, item)):
                    if (item != "include") and (not "common" in item) and (item != device):
                        rmtree(path_boards + item)

        except Exception as e:
            logging(str(e))
        
        for operation in single_copy_operations:
            
            #remove file from path, because it shouldnt be created as directory
            copy_dest_path = temporary_directory + operation[1]
            index = copy_dest_path.rindex("/")
            path_to_create = copy_dest_path[:index]
            create_directories(path_to_create)
            
            copyfile(operation[0], copy_dest_path)
        
        return dest_path
    
    except Exception as e:
        logging.error(str(e))
    
    return None
    
def zip_repo(src_path, dest_path):
    
    try:
        tar = tarfile.open(dest_path, "w:gz")
        for file_name in glob.glob(os.path.join(src_path, "*")):
            tar.add(file_name, os.path.basename(file_name))

        tar.close()
        
    except Exception as e:
        logging.error(str(e))
    
    return dest_path
    
def file_as_base64(path):
    
    with open(path, "rb") as file:
        return base64.b64encode(file.read())
    
def get_temporary_directory(ticket_id):
    
    return "tmp/{!s}/".format(ticket_id)
    
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
    
def get_application_name(id):
    
    db_cursor.execute("SELECT name FROM applications WHERE id=%s", (id,))
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
            logging.error(str(e))
            raise
        
def execute_makefile(path, device):
    
    # make does preserve the path when changing via "--directory=dir"
    
    proc = subprocess.Popen(["make", "--directory={!s}".format(path)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    build_result["cmd_output"] += proc.communicate()[0].replace("\n", "<br>")
    
    return

if __name__ == "__main__":
    
    logging.basicConfig(filename = "log/build_example_log.txt", format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)
    
    try:
        init_db()
        
        main(sys.argv[1])
        
        close_db()
        
    except Exception as e:
        logging.error(str(e), exc_info=True)
    