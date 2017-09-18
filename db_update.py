#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os

import config.db_config as config
from MyDatabase import MyDatabase

db = MyDatabase()


def main():

    update_modules()
    update_boards()
    update_applications()


def update_modules():
    
    db.query("TRUNCATE modules")
    
    for i in range(len(config.module_directories)):

        module_directory = config.module_directories[i]
        path = config.path_root + module_directory + "/"

        for item in os.listdir(path):
            if not os.path.isfile(os.path.join(path, item)):

                # ignoring include directories
                if item == "include":
                    continue
                    
                description = get_description(path, item)
                    
                module_name = get_name(path + item + "/", item)
                
                sql = "INSERT INTO modules (name, path, description, group_identifier) VALUES (%s, %s, %s, %s);"
                db.query(sql, (module_name, path + item + "/", description, module_directory))

    db.commit()


def update_boards():

    db.query("TRUNCATE boards")
    
    path = config.path_root + "boards/"

    for item in os.listdir(path):
        if not os.path.isfile(os.path.join(path, item)) and not item.endswith("-common"):
            
            sql = "INSERT INTO boards (display_name, internal_name, flash_program) VALUES (%s, %s, %s);"
            db.query(sql, (item, item, "openocd"))
            
    db.commit()


def update_applications():

    db.query("TRUNCATE applications")
    
    for i in range(len(config.application_directories)):

        application_directory = config.application_directories[i]
        path = config.path_root + application_directory + "/"

        for item in os.listdir(path):
            if not os.path.isfile(os.path.join(path, item)):

                # ignoring include directories
                if item == "include":
                    continue
                    
                description = get_description(path, item)
                    
                application_name = get_name(path + item + "/", item)
                
                sql = "INSERT INTO applications (name, path, description, group_identifier) VALUES (%s, %s, %s, %s);"
                db.query(sql, (application_name, path + item + "/", description, application_directory))

    db.commit()


def get_description(path, item):
    
    def get_description_helper(path):
        
        description = ""
    
        try:
            with open(path) as file:
                
                brief_active = False
                for line in file:
                    
                    if brief_active:
                        if not "* @" in line:
                            description += line.replace("*", "", 1).strip()
                        else:
                            break
                    
                    if "@brief" in line:
                        index = line.find("@brief") + len("@brief")
                        description = line[index:].strip()
                        brief_active = True

        except IOError:
            return None

        if description == "":
            description = None
            
        return description
        
    # try rule 1
    description = get_description_helper(path + "include/" + item +".h")
        
    # try rule 2
    if description is None:
        description = get_description_helper(path + item + "/" + "doc.txt")

    # try rule 3
    if description is None:
        description = get_description_helper(path + item + "/" + item + ".c")

    # try rule 4
    if description is None:
        description = get_description_helper(path + item + "/" + "main.c")
        
    return description


def get_name(path, application_directory):
    
    name = ""
    
    try:
        with open(path + "Makefile") as makefile:
            for line in makefile:
                
                line = line.replace(" ", "")
                
                if "APPLICATION=" in line:
                    index = line.find("APPLICATION=") + len("APPLICATION=")
                    name = line[index:]
                    break
                    
                elif "PKG_NAME=" in line:
                    index = line.find("PKG_NAME=") + len("PKG_NAME=")
                    name = line[index:]
                    break
    
    except IOError:
        return application_directory
    
    if name == "":
        name = application_directory
    
    # remove \n and stuff like that
    return name.strip()


if __name__ == "__main__":

    main()