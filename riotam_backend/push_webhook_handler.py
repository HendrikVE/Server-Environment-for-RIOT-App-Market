#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function

import logging
import os
from subprocess import Popen, PIPE, STDOUT

CUR_DIR = os.path.abspath(os.path.dirname(__file__))
PATH_RIOTAM_BACKEND = os.path.normpath(os.path.join(CUR_DIR, ".."))
LOGFILE = os.path.join(PATH_RIOTAM_BACKEND, "log", "push_webhook_handler_log.txt")


def main():
    """
    Routine to update backend repository. Gets called by push_webhook_handler.py inside frontend"""

    """UPDATE GIT REPOSITORY"""
    output = execute_command(["git", "-C", PATH_RIOTAM_BACKEND, "pull"])
    logging.debug("PULL BACKEND REPO:\n" + output)

    output = execute_command(["git", "-C", PATH_RIOTAM_BACKEND, "submodule", "update", "--recursive", "--remote"])
    logging.debug("UPDATE SUBMODULES:\n" + output)

    """SETUP DATABASE"""
    output = execute_command(["python", "db_create.py"], os.path.join(PATH_RIOTAM_BACKEND, "riotam_backend", "setup"))
    logging.debug("DB_CREATE:\n" + output)

    output = execute_command(["python", "db_setup.py"], os.path.join(PATH_RIOTAM_BACKEND, "riotam_backend", "setup"))
    logging.debug("DB_SETUP:\n" + output)

    """UPDATE DATABASE"""
    output = execute_command(["python", "db_update.py"], os.path.join(PATH_RIOTAM_BACKEND, "riotam_backend", "tasks", "database"))
    logging.debug("DB_UPDATE:\n" + output)

    """CREATE STRIPPED RIOT REPOSITORY"""
    output = execute_command(["python", "strip_riot_repo.py"], os.path.join(PATH_RIOTAM_BACKEND, "riotam_backend"))
    logging.debug("STRIP_RIOT_REPO.py:\n" + output)

    # give calling script from frontend an answer
    print("updated backend sucessfully")


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

    logging.basicConfig(filename=LOGFILE, format="%(asctime)s [%(levelname)s]: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)

    try:
        main()

    except Exception as e:
        logging.error(str(e), exc_info=True)