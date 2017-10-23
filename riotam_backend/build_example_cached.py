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
    "output_archive": None,
    "success": False,
    "extra": None
}

LOGFILE = os.path.join(PROJECT_ROOT_DIR, "log", "build_example_cached_log.txt")
LOGFILE = os.environ.get("BACKEND_LOGFILE", LOGFILE)

CACHE_DIR = os.path.join(PROJECT_ROOT_DIR, ".cache")

db = MyDatabase()


def main(argv):

    parser = init_argparse()

    try:
        args = parser.parse_args(argv)

    except Exception as e:
        build_result["cmd_output"] += str(e)
        return

    bu.create_directories(CACHE_DIR)

    board = args.board
    application_id = args.application

    build_result["board"] = board

    used_modules = get_used_modules(application_id)

    app_build_parent_dir = os.path.join(PROJECT_ROOT_DIR, "RIOT", "generated_by_riotam")

    # unique application directory name
    ticket_id = bu.get_ticket_id()

    app_name = "application%s" % ticket_id
    app_build_dir = os.path.join(app_build_parent_dir, app_name)

    temp_dir = bu.get_temporary_directory(PROJECT_ROOT_DIR, ticket_id)

    build_result["application_name"] = app_name

    app_path = os.path.join(PROJECT_ROOT_DIR, fetch_application_path(application_id))
    copytree(app_path, app_build_dir)

    app_build_dir_abs_path = os.path.abspath(app_build_dir)
    bindir = bu.get_bindir(app_build_dir_abs_path, board)

    for module in used_modules:
        cached_module_path = get_cache_entry(board, module)

        if cached_module_path is not None:

            build_result["extra"] = "using cache entry from %s" % cached_module_path

            dest_path_module = os.path.join(bindir, module)

            try:
                rmtree(dest_path_module)
            except:
                pass

            copytree(cached_module_path, dest_path_module)

    replace_application_name(os.path.join(app_build_dir, "Makefile"), app_name)

    build_result["cmd_output"] += bu.execute_makefile(app_build_dir, board, app_name)

    try:
        stripped_repo_path = bu.generate_stripped_repo(app_build_dir, PROJECT_ROOT_DIR, temp_dir, board, app_name)

        archive_path = os.path.join(temp_dir, "RIOT_stripped.tar")
        bu.zip_repo(stripped_repo_path, archive_path)

        archive_extension = "tar"

        build_result["output_archive_extension"] = archive_extension
        build_result["output_archive"] = bu.file_as_base64(archive_path)

        build_result["success"] = True

        # cache modules of successful tasks
        for module in used_modules:
            cache_module(app_build_dir, board, module)

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


def get_cache_entry(board, module_name):

    cache_path = os.path.join(CACHE_DIR, board, module_name)
    ready_to_use_file = os.path.join(cache_path, ".ready_to_use")

    if os.path.isfile(ready_to_use_file):
        return cache_path

    else:
        return None


def cache_module(app_build_dir, board, module_name):

    # only store if not in cache already
    if get_cache_entry(board, module_name) is None:

        # set ELFFILE the same way as RIOT Makefile.include (path to .hex file is extracted from this information)
        app_build_dir_abs_path = os.path.abspath(app_build_dir)

        bindirbase = bu.get_bindirbase(app_build_dir_abs_path)
        bindir = os.path.join(bindirbase, board)

        module_path = os.path.join(bindir, module_name)
        dest_in_cache = os.path.join(CACHE_DIR, board, module_name)

        copytree(module_path, dest_in_cache)

        # show that cached module is now ready to use
        ready_file_path = os.path.join(dest_in_cache, ".ready_to_use")
        open(ready_file_path, "a").close()


def get_used_modules(app_id):

    db.query("SELECT * FROM applications where id='%s'" % app_id)
    applications = db.fetchall()

    return get_modules_from_makefile(applications[0]["path"])


def get_modules_from_makefile(path_to_makefile):

    modules = []

    path_to_makefile = os.path.join(path_to_makefile, "Makefile")

    with open(path_to_makefile) as make_file:

        for line in make_file:

            line = line.strip()
            if line.startswith("USEMODULE"):
                index_begin = line.rfind(" ")
                modules.append(line[index_begin+1:])

    return modules


if __name__ == "__main__":

    logging.basicConfig(filename=LOGFILE, format="%(asctime)s [%(levelname)s]: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)

    try:
        main(sys.argv[1:])

    except Exception as e:
        logging.error(str(e), exc_info=True)
        build_result["cmd_output"] += str(e)

    print(build_result)
