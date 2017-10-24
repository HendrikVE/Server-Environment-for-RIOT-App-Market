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

from config import config
from utility import build_utility as b_util
from utility import application_info_utility as a_util
from common.MyDatabase import MyDatabase
from common.ModuleCache import ModuleCache

build_result = {
    "cmd_output": "",
    "board": None,
    "application_name": "application",
    "output_archive": None,
    "success": False
}

LOGFILE = os.path.join(PROJECT_ROOT_DIR, "log", "build_example.log")
LOGFILE = os.environ.get("BACKEND_LOGFILE", LOGFILE)

db = MyDatabase()

cache_dir = os.path.join(PROJECT_ROOT_DIR, ".cache")
cache = ModuleCache(cache_dir)


def main(argv):

    parser = init_argparse()

    try:
        args = parser.parse_args(argv)

    except Exception as e:
        build_result["cmd_output"] += str(e)
        return

    board = args.board
    application_id = args.application
    using_cache = args.caching

    build_result["board"] = board

    app_build_parent_dir = os.path.join(PROJECT_ROOT_DIR, "RIOT", "generated_by_riotam")

    # unique application directory name
    ticket_id = b_util.get_ticket_id()

    app_name = "application%s" % ticket_id
    app_build_dir = os.path.join(app_build_parent_dir, app_name)

    temp_dir = b_util.get_temporary_directory(PROJECT_ROOT_DIR, ticket_id)

    build_result["application_name"] = app_name

    app_path = os.path.join(PROJECT_ROOT_DIR, a_util.get_application_path(db, application_id))
    copytree(app_path, app_build_dir)

    used_modules = None
    if using_cache:

        used_modules = a_util.get_defined_modules(db, application_id)

        app_build_dir_abs_path = os.path.abspath(app_build_dir)
        bindir = b_util.get_bindir(app_build_dir_abs_path, board)

        for module in used_modules:
            cached_module_path = cache.get_cache_entry(board, module)

            if cached_module_path is not None:

                dest_path_module = os.path.join(bindir, module)

                try:
                    rmtree(dest_path_module)

                except:
                    pass

                copytree(cached_module_path, dest_path_module)

    replace_application_name(os.path.join(app_build_dir, "Makefile"), app_name)

    build_result["cmd_output"] += b_util.execute_makefile(app_build_dir, board, app_name)

    try:
        stripped_repo_path = b_util.generate_stripped_repo(app_build_dir, PROJECT_ROOT_DIR, temp_dir, board, app_name)

        archive_path = os.path.join(temp_dir, "RIOT_stripped.tar")
        b_util.zip_repo(stripped_repo_path, archive_path)

        archive_extension = "tar"

        build_result["output_archive_extension"] = archive_extension
        build_result["output_archive"] = b_util.file_as_base64(archive_path)

        build_result["success"] = True

        if using_cache:
            # cache modules of successful tasks
            for module in used_modules:
                cache.cache_module(app_build_dir, board, module)

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

    parser.add_argument("--caching",
                        dest="caching", action="store_true", default=False,
                        required=False,
                        help="wether to use cache or not")

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


if __name__ == "__main__":

    logging.basicConfig(filename=LOGFILE, format=config.LOGGING_FORMAT,
                        datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)

    try:
        main(sys.argv[1:])

    except Exception as e:
        logging.error(str(e), exc_info=True)
        build_result["cmd_output"] += str(e)

    print(build_result)
