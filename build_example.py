#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function

import argparse
import json
import logging
import os
import sys
from shutil import copytree, rmtree, copyfile

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
    application_id = args.application

    build_result["board"] = board

    parent_path = "RIOT/generated_by_riotam"

    # unique application directory name
    ticket_id = bu.get_ticket_id()

    application_name = "application%s" % ticket_id
    full_path = os.path.join(parent_path, application_name)

    temporary_directory = bu.get_temporary_directory(ticket_id)

    build_result["application_name"] = application_name

    application_path = fetch_application_path(application_id)
    copytree(application_path, full_path)

    replace_application_name(os.path.join(full_path, "Makefile"), application_name)

    build_result["cmd_output"] += bu.execute_makefile(full_path, board)

    try:
        """ IMAGE FILE """
        file_extension = "elf"  # TODO: or hex
        build_result["output_file_extension"] = file_extension

        binary_path = os.path.join(full_path, "bin", board, application_name + "." + file_extension)
        build_result["output_file"] = bu.file_as_base64(binary_path)

        """ ARCHIVE FILE """
        archive_extension = "tar"
        build_result["output_archive_extension"] = archive_extension

        binary_dest_path = binary_path.replace("RIOT", "RIOT_stripped")
        makefile_dest_path = full_path.replace("RIOT", "RIOT_stripped")

        # [(src_path, dest_path)]
        single_copy_operations = [
            (binary_path, binary_dest_path),
            (os.path.join(full_path, "Makefile"), os.path.join(makefile_dest_path, "Makefile"))
        ]

        stripped_repo_path = bu.prepare_stripped_repo("RIOT_stripped/", temporary_directory, single_copy_operations, board)

        archive_path = os.path.join(temporary_directory, "RIOT_stripped.tar")
        bu.zip_repo(stripped_repo_path, archive_path)

        build_result["output_archive"] = bu.file_as_base64(archive_path)

    except Exception as e:
        logging.error(str(e), exc_info=True)
        build_result["cmd_output"] += "something went wrong on server side"

    # using iframe for automatic start of download, https://stackoverflow.com/questions/14886843/automatic-download-launch
    # build_result["cmd_output"] += "<div style=""display:none;""><iframe id=""frmDld"" src=""timer_periodic_wakeup.elf""></iframe></div>"

    # delete temporary directories after finished build
    try:
        #rmtree(full_path)
        #rmtree(temporary_directory)
        pass

    except Exception as e:
        logging.error(str(e), exc_info=True)


def init_argparse():

    parser = argparse.ArgumentParser(description="Build RIOT OS")

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


def replace_application_name(path, application_name):
    """
    Replace application name in line which starts with "APPLICATION="

    Parameters
    ----------
    path: string
        Path to the file

    application_name: string
        Name of the application

    """

    # Save the old one to check later in case there is an error
    copyfile(path, path + ".old")

    with open(path + ".old", "r") as old_makefile:
        with open(path, "w") as makefile:

            for line in old_makefile.readlines():
                if line.replace(" ", "").startswith("APPLICATION="):
                    line = "APPLICATION = %s\n" % application_name

                makefile.write(line)


def fetch_application_path(id):
    """
    Fetch path of application from database

    Parameters
    ----------
    id: int
        ID of the application

    Returns
    -------
    string
        Path of the application, None if not found

    """
    db.query("SELECT path FROM applications WHERE id=%s", (id,))
    applications = db.fetchall()

    if len(applications) != 1:
        logging.error("error in database: len(applications != 1)")
        return None

    else:
        return applications[0]["path"]


if __name__ == "__main__":
    
    logging.basicConfig(filename=LOGFILE, format="%(asctime)s [%(levelname)s]: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)

    try:
        main(sys.argv[1:])

    except Exception as e:
        logging.error(str(e), exc_info=True)
        build_result["cmd_output"] += str(e)

    print (json.dumps(build_result))
