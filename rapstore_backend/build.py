#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
 * Copyright (C) 2017 Hendrik van Essen
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
"""

from __future__ import print_function

import argparse
import logging
import os
import sys
from shutil import rmtree, copytree

# append root of the python code tree to sys.apth so that imports are working
#   alternative: add path to rapstore_backend to the PYTHONPATH environment variable, but this includes one more step
#   which could be forget
CUR_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_DIR = os.path.normpath(os.path.join(CUR_DIR, os.pardir))
sys.path.append(PROJECT_ROOT_DIR)

from config import config
from utility import build_utility as b_util
from common.MyDatabase import MyDatabase
from common.BuildResult import get_build_result_template

LOGFILE = os.path.join(PROJECT_ROOT_DIR, 'log', 'build.log')
LOGFILE = os.environ.get('BACKEND_LOGFILE', LOGFILE)

build_result = get_build_result_template()
db = MyDatabase()


def main(argv):

    parser = init_argparse()

    try:
        args = parser.parse_args(argv)

    except Exception as e:
        build_result['cmd_output'] += str(e)
        return

    board = args.board
    modules = args.modules
    main_file_content = args.main_file_content
    using_cache = args.caching

    build_result['board'] = board

    app_build_parent_dir = os.path.join(PROJECT_ROOT_DIR, 'RIOT', 'generated_by_riotam')

    # unique application directory name
    ticket_id = b_util.get_ticket_id()

    app_name = 'application%s' % ticket_id
    app_build_dir = os.path.join(app_build_parent_dir, app_name)

    temp_dir = b_util.get_temporary_directory(PROJECT_ROOT_DIR, ticket_id)

    build_result['application_name'] = app_name

    b_util.create_directories(app_build_dir)

    write_makefile(board, modules, app_name, app_build_dir)

    with open(os.path.join(app_build_dir, 'main.c'), 'w') as main_file:
        main_file.write(main_file_content)

    build_result['cmd_output'] += b_util.execute_makefile(app_build_dir, board, app_name)

    try:
        stripped_repo_path = b_util.generate_stripped_repo(app_build_dir, PROJECT_ROOT_DIR, temp_dir, board, app_name)

        archive_path = os.path.join(temp_dir, 'RIOT_stripped.tar')
        b_util.zip_repo(stripped_repo_path, archive_path)

        archive_extension = 'tar'

        build_result['output_archive_extension'] = archive_extension
        build_result['output_archive'] = b_util.file_as_base64(archive_path)

        build_result['success'] = True

    except Exception as e:
        logging.error(str(e), exc_info=True)
        build_result['cmd_output'] += 'something went wrong on server side'

    # delete temporary directories after finished build
    try:
        rmtree(app_build_dir)
        rmtree(temp_dir)

    except Exception as e:
        logging.error(str(e), exc_info=True)


def init_argparse():

    parser = argparse.ArgumentParser(description='Build RIOT OS')

    parser.add_argument('--modules',
                        dest='modules', action='store',
                        type=int,
                        required=True,
                        nargs='+',
                        help='modules to build in to the image')

    parser.add_argument('--board',
                        dest='board', action='store',
                        required=True,
                        help='the board for which the image should be made')

    parser.add_argument('--mainfile',
                        dest='main_file_content', action='store',
                        required=True,
                        help='main.c file for compiling custom RIOT OS')

    parser.add_argument('--caching',
                        dest='caching', action='store_true', default=False,
                        required=False,
                        help='wether to use cache or not')

    return parser


def fetch_module_name(id):
    """
    Fetch module name from database

    Parameters
    ----------
    id: int
        ID of the module

    Returns
    -------
    string
        Name of the module, None if not found

    """
    db.query('SELECT name FROM modules WHERE id=%s', (id,))
    names = db.fetchall()

    if len(names) != 1:
        logging.error('error in database: len(names != 1)')
        return None

    else:
        return names[0]['name']


def write_makefile(board, modules, application_name, path):
    """
    Write a custom makefile including board and modules

    Parameters
    ----------
    board: string
        Board name
    modules: array_like with int
        List with IDs of wanted modules
    application_name: string
        Name ot the application
    path: string
        Path the makefile is written to

    """
    filename = 'Makefile'
    with open(os.path.join(path, filename), 'w') as makefile:

        makefile.write('APPLICATION = ' + application_name)
        makefile.write('\n\n')

        makefile.write('BOARD ?= %s' % board)
        makefile.write('\n\n')

        makefile.write('RIOTBASE ?= $(CURDIR)/../..')
        makefile.write('\n\n')
        
        for module in modules:
            module_name = fetch_module_name(module)

            if module_name is None:
                build_result['cmd_output'] += 'error while reading modules from database'
                break

            else :
                makefile.write('USEMODULE += %s\n' % module_name)

        makefile.write('\n')
        makefile.write('include $(RIOTBASE)/Makefile.include')


if __name__ == '__main__':
    
    logging.basicConfig(filename=LOGFILE, format=config.LOGGING_FORMAT,
                        datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

    try:
        main(sys.argv[1:])
        
    except Exception as e:
        logging.error(str(e), exc_info=True)
        build_result['cmd_output'] += str(e)

    print(build_result)
