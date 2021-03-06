#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
 * Copyright (C) 2017 Hendrik van Essen
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
"""

import os
import sys

# append root of the python code tree to sys.apth so that imports are working
#   alternative: add path to rapstore_backend to the PYTHONPATH environment variable, but this includes one more step
#   which could be forget
CUR_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_DIR = os.path.normpath(os.path.join(CUR_DIR, os.pardir, os.pardir, os.pardir))
sys.path.append(PROJECT_ROOT_DIR)

from rapstore_backend.config import config
from rapstore_backend.common.MyDatabase import MyDatabase
import replace_board_display_names as rbdn

db = MyDatabase()


def main():

    update_modules()
    update_boards()
    update_applications()

    # now update the overwritten board display names
    rbdn.main()


def update_modules():
    """
    Update table "modules". The table is truncated and data is re-imported

    """
    
    db.query('TRUNCATE modules')
    
    for i in range(len(config.module_directories)):

        module_directory = config.module_directories[i]
        module_path = os.path.join(PROJECT_ROOT_DIR, config.path_root, module_directory)

        for name in os.listdir(module_path):
            if not os.path.isfile(os.path.join(module_path, name)):

                # ignoring include directories
                if name == 'include':
                    continue
                    
                description = get_description(module_path, name)
                    
                module_name = get_name(os.path.join(module_path, name), name)
                
                sql = 'INSERT INTO modules (name, path, description, group_identifier) VALUES (%s, %s, %s, %s);'
                db.query(sql, (module_name, os.path.join(module_path, name), description, module_directory))

    db.commit()


def update_boards():
    """
    Update table "boards". The table is truncated and data is re-imported

    """

    def is_valid_board(path, item):
        """
        A board is valid if:
            1. path is a directory
            2. path doesn't end with "<prefix>-common"
            3. board is not native
        """
        return (
                not os.path.isfile(os.path.join(path, item))
                and not item.endswith('-common')
                and not item == 'common'
                and not item == 'native'
        )

    db.query('TRUNCATE boards')
    
    path = os.path.join(PROJECT_ROOT_DIR, config.path_root, 'boards')

    for item in os.listdir(path):
        if is_valid_board(path, item):
            
            sql = 'INSERT INTO boards (display_name, internal_name, flash_program) VALUES (%s, %s, %s);'
            db.query(sql, (item, item, 'openocd'))
            
    db.commit()


def update_applications():
    """
    Update table "applications". The table is truncated and data is re-imported

    """

    db.query('TRUNCATE applications')
    
    for i in range(len(config.application_directories)):

        application_directory = config.application_directories[i]
        application_path = os.path.join(PROJECT_ROOT_DIR, config.path_root, application_directory)

        for name in os.listdir(application_path):
            if not os.path.isfile(os.path.join(application_path, name)):

                # ignoring include directories
                if name == 'include':
                    continue
                    
                description = get_description(application_path, name)
                    
                application_name = get_name(os.path.join(application_path, name), name)
                
                sql = 'INSERT INTO applications (name, path, description, group_identifier) VALUES (%s, %s, %s, %s);'
                db.query(sql, (application_name, os.path.join(application_path, name), description, application_directory))

    db.commit()


def get_description(path, name):
    """
    Collection of rules executing inner function to search for a description

    Parameters
    ----------
    path: string
        Path in which the search is done
    name: string
        Name of a directory

    Returns
    -------
    string
        Description of item, None if not found

    """
    
    def get_description_helper(path):
        """
        Get description from line which contains "@brief"

        Parameters
        ----------
        path: string
            Path to file

        Returns
        -------
        string
            Description of item, None if not found

        """
        
        description = ''
    
        try:
            with open(path) as file:
                
                brief_active = False
                for line in file:
                    
                    if brief_active:
                        if not '* @' in line:
                            description += line.replace('*', '', 1).strip()
                        else:
                            break
                    
                    if '@brief' in line:
                        index = line.find('@brief') + len('@brief')
                        description = line[index:].strip()
                        brief_active = True

        except IOError:
            return None

        if description == '':
            description = None
            
        return description
        
    # try rule 1
    description = get_description_helper(os.path.join(path, 'include', name + '.h'))
        
    # try rule 2
    if description is None:
        description = get_description_helper(os.path.join(path, name, 'doc.txt'))

    # try rule 3
    if description is None:
        description = get_description_helper(os.path.join(path, name, name + '.c'))

    # try rule 4
    if description is None:
        description = get_description_helper(os.path.join(path, name, 'main.c'))
        
    return description


def get_name(path, application_directory):
    """"
    Get the name of an application

    Parameters
    ----------
    path: string
        Path containing file called "Makefile"
    application_directory: string
        Replacement if nothing found or IOError is raised internally

    Returns
    -------
    string
        Name of the application

    """
    name = ''
    
    try:
        with open(os.path.join(path, 'Makefile')) as makefile:
            for line in makefile:
                
                line = line.replace(' ', '')
                
                if 'APPLICATION=' in line:
                    index = line.find('APPLICATION=') + len('APPLICATION=')
                    name = line[index:]
                    break
                    
                elif 'PKG_NAME=' in line:
                    index = line.find('PKG_NAME=') + len('PKG_NAME=')
                    name = line[index:]
                    break
    
    except IOError:
        return application_directory
    
    if name == '':
        name = application_directory
    
    # remove \n and stuff like that
    return name.strip()


if __name__ == '__main__':

    main()
