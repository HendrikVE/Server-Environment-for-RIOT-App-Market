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

import logging
import os
from shutil import rmtree
from subprocess import Popen, PIPE, STDOUT

from config import config

CUR_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_DIR = os.path.normpath(os.path.join(CUR_DIR, os.pardir))

LOGFILE = os.path.join(PROJECT_ROOT_DIR, "log", "push_webhook_handler.log")


def main():
    """
    Routine to update backend repository. Gets called by push_webhook_handler.py inside frontend"""

    """DELETE CACHE"""
    cache_dir = config.APPLICATION_CACHE_DIR
    try:
        rmtree(cache_dir)

    except Exception:
        pass

    """UPDATE GIT REPOSITORY"""
    output = execute_command(["git", "-C", PROJECT_ROOT_DIR, "pull"])
    logging.debug("PULL BACKEND REPO:\n" + output)

    output = execute_command(["git", "-C", PROJECT_ROOT_DIR, "submodule", "update", "--recursive", "--remote"])
    logging.debug("UPDATE SUBMODULES:\n" + output)

    """SETUP DATABASE"""
    output = execute_command(["python", "db_create.py"], os.path.join(PROJECT_ROOT_DIR, "riotam_backend", "setup"))
    logging.debug("DB_CREATE:\n" + output)

    output = execute_command(["python", "db_setup.py"], os.path.join(PROJECT_ROOT_DIR, "riotam_backend", "setup"))
    logging.debug("DB_SETUP:\n" + output)

    """UPDATE DATABASE"""
    output = execute_command(["python", "db_update.py"], os.path.join(PROJECT_ROOT_DIR, "riotam_backend", "tasks", "database"))
    logging.debug("DB_UPDATE:\n" + output)

    """CREATE STRIPPED RIOT REPOSITORY"""
    output = execute_command(["python", "strip_riot_repo.py"], os.path.join(PROJECT_ROOT_DIR, "riotam_backend"))
    logging.debug("STRIP_RIOT_REPO.py:\n" + output)

    # give calling script from frontend an answer
    print("updated backend successfully")


def execute_command(cmd, cwd=None):
    """
    Execute command with Popen

    Parameters
    ----------
    cmd: array_like
        List of strings of the command to execute. Needs to be split on spaces
    cwd: string
        working directory to change to (default is None)

    Returns
    -------
    string
        Commandline output

    """
    process = Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=cwd)
    return process.communicate()[0]


if __name__ == "__main__":

    logging.basicConfig(filename=LOGFILE, format=config.LOGGING_FORMAT,
                        datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)

    try:
        main()

    except Exception as e:
        logging.error(str(e), exc_info=True)
