#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import config.db_config as config
import utility.build_utility as build_utility

import sys, time
from shutil import copyfile, rmtree
import json
import MySQLdb
import logging
import argparse
import uuid

db = None
db_cursor = None

build_result = {
    "cmd_output": "",
    "board": None,
    "application_name": "application",
    "output_file": None,
    "output_file_extension": None,
    "output_archive": None,
    "output_archive_extension": None
}


def main(argv):

    parser = init_argparse()

    try:
        args = parser.parse_args(argv)

    except Exception as e:
        build_result["cmd_output"] += str(e)
        return

    init_db()

    board = args.board
    modules = args.modules

    build_result["board"] = board

    parent_path = "RIOT/generated_by_riotam/"

    # unique application directory name
    ticket_id = str(time.time()) + str(uuid.uuid1())

    application_name = "application{!s}".format(ticket_id)
    application_path = application_name + "/"
    full_path = parent_path + application_path

    temporary_directory = build_utility.get_temporary_directory(ticket_id)

    build_result["application_name"] = application_name

    build_utility.create_directories(full_path)

    write_makefile(board, modules, application_name, full_path)

    # just for testing!
    copyfile("main.c", full_path + "main.c")

    build_result["cmd_output"] += build_utility.execute_makefile(full_path)

    try:
        """ IMAGE FILE """
        file_extension = "elf"  # TODO: or hex
        build_result["output_file_extension"] = file_extension

        binary_path = full_path + "bin/" + board + "/" + application_name + "." + file_extension
        build_result["output_file"] = build_utility.file_as_base64(binary_path)

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

        stripped_repo_path = build_utility.prepare_stripped_repo("RIOT_stripped/", temporary_directory, single_copy_operations,
                                                   board)
        archive_path = build_utility.zip_repo(stripped_repo_path, temporary_directory + "RIOT_stripped.tar")

        build_result["output_archive"] = build_utility.file_as_base64(archive_path)

    except Exception as e:
        logging.error(str(e))
        build_result["cmd_output"] += "something went wrong on server side"

    # using iframe for automatic start of download, https://stackoverflow.com/questions/14886843/automatic-download-launch
    # build_result["cmd_output"] += "<div style=""display:none;""><iframe id=""frmDld"" src=""timer_periodic_wakeup.elf""></iframe></div>"

    close_db()

    # delete temporary directories after finished build
    try:
        rmtree(full_path)
        rmtree(temporary_directory)

    except Exception as e:
        logging.error(str(e))


def init_argparse():

    parser = argparse.ArgumentParser(description='Build RIOT OS')

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

    return parser


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


def write_makefile(board, modules, application_name, path):

    filename = "Makefile"
    with open(path + filename, "w") as makefile:

        makefile.write("APPLICATION = " + application_name)
        makefile.write("\n\n")

        # TODO: check, if board is in database!!!
        makefile.write("BOARD ?= {!s}".format(board))
        makefile.write("\n\n")

        makefile.write("RIOTBASE ?= $(CURDIR)/../..")
        makefile.write("\n\n")
        
        for module in modules:
            module_name = get_module_name(module)

            if module_name is None:
                build_result["cmd_output"] += "error while reading modules from database"
                break

            else :
                makefile.write("USEMODULE += {!s}\n".format(module_name))

        makefile.write("\n")
        makefile.write("include $(RIOTBASE)/Makefile.include")


if __name__ == "__main__":
    
    logging.basicConfig(filename = "log/build_log.txt", format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)

    try:
        main(sys.argv[1:])
        
    except Exception as e:
        logging.error(str(e), exc_info=True)
        build_result["cmd_output"] += str(e)

    print json.dumps(build_result)
