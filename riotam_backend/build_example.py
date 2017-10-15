#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function

import argparse
import logging
import os
import sys
from shutil import copytree, rmtree, copyfile

# append root of the python code tree to sys.apth so that imports are working
#   alternative: add path to riotam_backend to the PYTHONPATH environment variable, but this includes one more step
#   which could be forget
CUR_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_DIR = os.path.normpath(os.path.join(CUR_DIR, ".."))
sys.path.append(PROJECT_ROOT_DIR)

from riotam_backend.utility import build_utility as bu
from riotam_backend.common.MyDatabase import MyDatabase

build_result = {
    "cmd_output": "",
    "board": None,
    "application_name": "application",
    "output_file": None,
    "output_file_extension": None,
    "output_archive": None,
    "output_archive_extension": None,
    "success": False
}

LOGFILE = os.path.join(PROJECT_ROOT_DIR, "log", "build_example_log.txt")
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

    app_build_parent_dir = os.path.join(PROJECT_ROOT_DIR, "RIOT", "generated_by_riotam")

    # unique application directory name
    ticket_id = bu.get_ticket_id()

    app_name = "application%s" % ticket_id
    app_build_dir = os.path.join(app_build_parent_dir, app_name)

    temp_dir = bu.get_temporary_directory(PROJECT_ROOT_DIR, ticket_id)

    build_result["application_name"] = app_name

    app_path = os.path.join(PROJECT_ROOT_DIR, fetch_application_path(application_id))
    copytree(app_path, app_build_dir)

    replace_application_name(os.path.join(app_build_dir, "Makefile"), app_name)

    build_result["cmd_output"] += bu.execute_makefile(app_build_dir, board, app_name)

    try:
        """ IMAGE FILE """
        file_extension = "elf"  # TODO: or hex
        build_result["output_file_extension"] = file_extension

        bindir = os.path.join(app_build_dir, "bin", board)
        elffile_path = bu.app_elffile_path(bindir, app_name)
        hexfile_path = bu.app_hexfile_path(bindir, app_name)

        # TODO: remove
        build_result["output_file"] = bu.file_as_base64(elffile_path)

        """ ARCHIVE FILE """
        archive_extension = "tar"
        build_result["output_archive_extension"] = archive_extension

        path = os.path.join(temp_dir, "RIOT_stripped", "generated_by_riotam", app_name)
        elffile_dest_path = bu.app_elffile_path(os.path.join(path, "bin", board), app_name)
        hexfile_dest_path = bu.app_hexfile_path(os.path.join(path, "bin", board), app_name)
        makefile_dest_path = path

        # [(src_path, dest_path)]
        single_copy_operations = [
            (elffile_path, elffile_dest_path),
            (hexfile_path, hexfile_dest_path),
            (os.path.join(app_build_dir, "Makefile"), os.path.join(makefile_dest_path, "Makefile"))
        ]

        path_stripped_riot = os.path.join(PROJECT_ROOT_DIR, "RIOT_stripped")
        stripped_repo_path = bu.prepare_stripped_repo(path_stripped_riot, os.path.join(temp_dir, "RIOT_stripped"), single_copy_operations, board)

        archive_path = os.path.join(temp_dir, "RIOT_stripped.tar")
        bu.zip_repo(stripped_repo_path, archive_path)

        build_result["output_archive"] = bu.file_as_base64(archive_path)
        build_result["success"] = True

    except Exception as e:
        logging.error(str(e), exc_info=True)
        build_result["cmd_output"] += "something went wrong on server side"

    # using iframe for automatic start of download, https://stackoverflow.com/questions/14886843/automatic-download-launch
    # build_result["cmd_output"] += "<div style=""display:none;""><iframe id=""frmDld"" src=""timer_periodic_wakeup.elf""></iframe></div>"

    # delete temporary directories after finished build
    try:
        rmtree(app_build_dir)
        rmtree(temp_dir)

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

    print(build_result)
