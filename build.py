#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function

import argparse
import json
import logging
import os
import sys
from shutil import copyfile, rmtree

import utility.build_utility as bu
from MyDatabase import MyDatabase

build_result = {
    "cmd_output": "",
    "board": None,
    "application_name": "application",
    "output_file": None,
    "output_file_extension": None,
    "output_archive": None,
    "output_archive_extension": None
}

CURDIR = os.path.dirname(__file__)

LOGFILE = os.path.join(CURDIR, "log/build_example_log.txt")
LOGFILE = os.environ.get("BACKEND_LOGFILE", LOGFILE)

db = MyDatabase()


def main(argv):

    parser = init_argparse()

    try:
        args = parser.parse_args(argv)

    except Exception as e:
        build_result["cmd_output"] += str(e)
        return

    board = args.board
    modules = args.modules
    main_file_content = args.main_file_content

    build_result["board"] = board

    parent_path = "RIOT/generated_by_riotam/"

    # unique application directory name
    ticket_id = bu.get_ticket_id()

    application_name = "application%s" % ticket_id
    application_path = application_name + "/"
    full_path = parent_path + application_path

    temporary_directory = bu.get_temporary_directory(ticket_id)

    build_result["application_name"] = application_name

    bu.create_directories(full_path)

    write_makefile(board, modules, application_name, full_path)

    with open(full_path + "main.c", "w") as main_file:
        main_file.write(main_file_content)

    build_result["cmd_output"] += bu.execute_makefile(full_path, board)

    try:
        """ IMAGE FILE """
        file_extension = "elf"  # TODO: or hex
        build_result["output_file_extension"] = file_extension

        binary_path = full_path + "bin/" + board + "/" + application_name + "." + file_extension
        build_result["output_file"] = bu.file_as_base64(binary_path)

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

        stripped_repo_path = bu.prepare_stripped_repo("RIOT_stripped/", temporary_directory, single_copy_operations, board)
        archive_path = bu.zip_repo(stripped_repo_path, temporary_directory + "RIOT_stripped.tar")

        build_result["output_archive"] = bu.file_as_base64(archive_path)

    except Exception as e:
        logging.error(str(e), exc_info=True)
        build_result["cmd_output"] += "something went wrong on server side"

    # using iframe for automatic start of download, https://stackoverflow.com/questions/14886843/automatic-download-launch
    # build_result["cmd_output"] += "<div style=""display:none;""><iframe id=""frmDld"" src=""timer_periodic_wakeup.elf""></iframe></div>"

    # delete temporary directories after finished build
    try:
        rmtree(full_path)
        rmtree(temporary_directory)

    except Exception as e:
        logging.error(str(e), exc_info=True)


def init_argparse():

    parser = argparse.ArgumentParser(description="Build RIOT OS")

    parser.add_argument("--modules",
                        dest="modules", action="store",
                        type=int,
                        required=True,
                        nargs="+",
                        help="modules to build in to the image")

    parser.add_argument("--board",
                        dest="board", action="store",
                        required=True,
                        help="the board for which the image should be made")

    parser.add_argument("--mainfile",
                        dest="main_file_content", action="store",
                        required=False,
                        help="main.c file for compiling custom RIOT OS")

    return parser


def fetch_module_name(id):
    
    db.query("SELECT name FROM modules WHERE id=%s", (id,))
    names = db.fetchall()

    if len(names) != 1:
        logging.error("error in database: len(names != 1)")
        return None

    else:
        return names[0]["name"]


def write_makefile(board, modules, application_name, path):

    filename = "Makefile"
    with open(path + filename, "w") as makefile:

        makefile.write("APPLICATION = " + application_name)
        makefile.write("\n\n")

        # TODO: check, if board is in database!!!
        makefile.write("BOARD ?= %s" % board)
        makefile.write("\n\n")

        makefile.write("RIOTBASE ?= $(CURDIR)/../..")
        makefile.write("\n\n")
        
        for module in modules:
            module_name = fetch_module_name(module)

            if module_name is None:
                build_result["cmd_output"] += "error while reading modules from database"
                break

            else :
                makefile.write("USEMODULE += %s\n" % module_name)

        makefile.write("\n")
        makefile.write("include $(RIOTBASE)/Makefile.include")


if __name__ == "__main__":
    
    logging.basicConfig(filename = "log/build_log.txt", format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)

    try:
        main(sys.argv[1:])
        
    except Exception as e:
        logging.error(str(e), exc_info=True)
        build_result["cmd_output"] += str(e)

    print (json.dumps(build_result))
