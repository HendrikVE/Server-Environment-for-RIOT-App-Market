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
from shutil import copytree, rmtree, copyfile

# append root of the python code tree to sys.apth so that imports are working
#   alternative: add path to riotam_backend to the PYTHONPATH environment variable, but this includes one more step
#   which could be forget
CUR_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_DIR = os.path.normpath(os.path.join(CUR_DIR, os.pardir))
sys.path.append(PROJECT_ROOT_DIR)

from config import config
from utility import build_utility as b_util
from utility import application_info_utility as a_util
from utility import module_info_utility as m_util
from common.MyDatabase import MyDatabase
from common.ModuleCache import ModuleCache
from common.ApplicationCache import ApplicationCache
from common.common import create_directories

build_result = {
    "cmd_output": "",
    "board": None,
    "application_name": "application",
    "output_archive": None,
    "success": False
}

LOGFILE = os.path.join(PROJECT_ROOT_DIR, "log", "build_example.log")
LOGFILE = os.environ.get("BACKEND_LOGFILE", LOGFILE)

MODULE_CACHE_DIR = os.path.join(PROJECT_ROOT_DIR, config.MODULE_CACHE_DIR)
APPLICATION_CACHE_DIR = os.path.join(PROJECT_ROOT_DIR, config.APPLICATION_CACHE_DIR)

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
    using_cache = args.caching
    prefetching = args.prefetching

    module_cache = ModuleCache(MODULE_CACHE_DIR)
    application_cache = ApplicationCache(APPLICATION_CACHE_DIR)

    source_app_name = a_util.get_application_name(db, application_id)
    source_app_dir_name = os.path.basename(a_util.get_application_path(db, application_id))

    build_result["board"] = board

    app_build_parent_dir = os.path.join(PROJECT_ROOT_DIR, "RIOT", "generated_by_riotam")

    # unique application directory name
    ticket_id = b_util.get_ticket_id()

    app_name = "application%s" % ticket_id
    app_build_dir = os.path.join(app_build_parent_dir, app_name)

    temp_dir = b_util.get_temporary_directory(PROJECT_ROOT_DIR, ticket_id)
    create_directories(temp_dir)

    build_result["application_name"] = app_name

    app_path = os.path.join(PROJECT_ROOT_DIR, a_util.get_application_path(db, application_id))
    copytree(app_path, app_build_dir)

    app_build_dir_abs_path = os.path.abspath(app_build_dir)
    bin_dir = b_util.get_bindir(app_build_dir_abs_path, board)

    used_modules = None
    cached_binaries = False
    if using_cache:

        cached_elffile_path = application_cache.get_entry(board, source_app_dir_name, "%s.elf" % source_app_name)
        cached_hexfile_path = application_cache.get_entry(board, source_app_dir_name, "%s.hex" % source_app_name)

        if (cached_elffile_path is not None) or (cached_hexfile_path is not None):

            cached_binaries = True

            create_directories(bin_dir)

            # copy files from cache in to bin_dir.
            # Need to rename it because further steps expect given name based on ticketID
            if cached_elffile_path is not None:
                copyfile(cached_elffile_path, os.path.join(bin_dir, "%s.elf" % app_name))

            if cached_hexfile_path is not None:
                copyfile(cached_hexfile_path, os.path.join(bin_dir, "%s.hex" % app_name))

        # check for cached modules (only, if no binaries were found)
        if not cached_binaries:
            used_module_names = a_util.get_defined_modules(db, application_id)

            used_modules = []
            for module_name in used_module_names:
                used_modules.append(m_util.get_module_id(db, module_name))

            prepare_modules_from_cache(module_cache, bin_dir, board, used_modules)

    if not cached_binaries:
        # if nothing found in cache, just build it
        replace_application_name(os.path.join(app_build_dir, "Makefile"), app_name)
        build_result["cmd_output"] += b_util.execute_makefile(app_build_dir, board, app_name)

    try:

        if not prefetching:
            stripped_repo_path = b_util.generate_stripped_repo(app_build_dir, PROJECT_ROOT_DIR, temp_dir, board, app_name)

            archive_path = os.path.join(temp_dir, "RIOT_stripped.tar")
            b_util.zip_repo(stripped_repo_path, archive_path)

            archive_extension = "tar"

            build_result["output_archive_extension"] = archive_extension
            build_result["output_archive"] = b_util.file_as_base64(archive_path)

            build_result["success"] = True

        else:

            # get compiled binaries
            elffile_path = b_util.app_elffile_path(bin_dir, app_name)
            hexfile_path = b_util.app_hexfile_path(bin_dir, app_name)

            if os.path.isfile(elffile_path) and os.path.isfile(hexfile_path):
                build_result["success"] = True

        app_build_dir_abs_path = os.path.abspath(app_build_dir)
        bin_dir = b_util.get_bindir(app_build_dir_abs_path, board)

        if using_cache and not cached_binaries:

            # cache modules of successful tasks
            cache_modules(module_cache, bin_dir, board, used_modules)

        if prefetching:
            # cache application
            cache_application(application_cache, bin_dir, temp_dir, board, app_name, source_app_name, source_app_dir_name)

    except Exception as e:
        logging.error(str(e), exc_info=True)
        build_result["cmd_output"] += "something went wrong on server side"

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

    parser.add_argument("--prefetching",
                        dest="prefetching", action="store_true", default=False,
                        required=False,
                        help="if flag is set, binaries are just generated and stored in application cache. Further steps are ignored")

    return parser


def prepare_modules_from_cache(cache, bin_dir, board, used_modules):

    for module in used_modules:

        module_dir_name = os.path.basename(m_util.get_module_path(db, module))
        cached_module_path = cache.get_entry(board, module_dir_name)

        if cached_module_path is not None:

            dest_path_module = os.path.join(bin_dir, module_dir_name)

            try:
                rmtree(dest_path_module)

            except:
                pass

            copytree(cached_module_path, dest_path_module)


def cache_modules(cache, bin_dir, board, used_modules):

    for module in used_modules:

        module_dir_name = os.path.basename(m_util.get_module_path(db, module))
        module_path = os.path.join(bin_dir, module_dir_name)
        cache.cache(module_path, board, module_dir_name)


def cache_application(cache, bin_dir, temp_dir, board, app_name, source_app_name, source_app_dir_name):

    # get compiled binaries
    elffile_path = b_util.app_elffile_path(bin_dir, app_name)
    hexfile_path = b_util.app_hexfile_path(bin_dir, app_name)

    # set new name for the file which should be cached with this name
    cached_elffile_name = "%s.elf" % source_app_name
    cached_hexfile_name = "%s.hex" % source_app_name

    # set path to files to be cached
    path_elffile_to_cache = os.path.join(temp_dir, cached_elffile_name)
    path_hexfile_to_cache = os.path.join(temp_dir, cached_hexfile_name)

    # copy files with new names to temp_dir
    try:
        copyfile(elffile_path, path_elffile_to_cache)
        # reference to renamed copy for caching purpose
        cache.cache(path_elffile_to_cache, board, source_app_dir_name, cached_elffile_name)
    except Exception as e:
        logging.debug(str(e))

    try:
        copyfile(hexfile_path, path_hexfile_to_cache)
        # reference to renamed copy for caching purpose
        cache.cache(path_hexfile_to_cache, board, source_app_dir_name, cached_hexfile_name)
    except Exception as e:
        logging.debug(str(e))


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
