#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import config.db_config as config
import utility.build_utility as bu

import MySQLdb
import sys, time
from shutil import copytree, rmtree
import json
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
    application_id = args.application

    build_result["board"] = board

    parent_path = "RIOT/generated_by_riotam/"

    # unique application directory name
    ticket_id = str(time.time()) + str(uuid.uuid1())

    application_name = "application{!s}".format(ticket_id)
    application_path = application_name + "/"
    full_path = parent_path + application_path

    temporary_directory = bu.get_temporary_directory(ticket_id)

    build_result["application_name"] = application_name

    application_display_name = get_application_name(application_id)
    copytree("RIOT/examples/" + application_display_name + "/", full_path)

    replace_application_name(full_path + "Makefile", application_name, board)

    build_result["cmd_output"] += bu.execute_makefile(full_path)

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

    close_db()

    # delete temporary directories after finished build
    try:
        rmtree(full_path)
        rmtree(temporary_directory)

    except Exception as e:
        logging.error(str(e), exc_info=True)


def init_argparse():

    parser = argparse.ArgumentParser(description='Build RIOT OS')

    parser.add_argument("--application",
                        dest="application", action="store",
                        type=int,
                        required=True,
                        help="modules to build in to the image")

    parser.add_argument("--board",
                        dest="board", action="store",
                        required=True,
                        help="the board for which the image should be made")

    return parser


def replace_application_name(path, application_name, board):
    
    file_content = []
    with open(path, "r") as makefile:

        file_content = list(makefile.readlines())

    with open(path, "w") as makefile:
        for line in file_content:

            if line.startswith("APPLICATION = "):
                makefile.write("APPLICATION = {!s}\n".format(application_name))
                
            elif line.startswith("BOARD ?="):
                makefile.write("BOARD = {!s}\n".format(board))
                
            else:
                makefile.write(line)


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
        logging.error("error in database: len(results != 1)")
        return None

    else:
        return results[0]["name"]


if __name__ == "__main__":
    
    logging.basicConfig(filename = "log/build_example_log.txt", format="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)

    try:
        main(sys.argv[1:])

    except Exception as e:
        logging.error(str(e), exc_info=True)
        build_result["cmd_output"] += str(e)

    print json.dumps(build_result)
