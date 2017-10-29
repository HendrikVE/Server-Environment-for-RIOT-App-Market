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

import ast
import logging
import multiprocessing
import os
import sys
from multiprocessing.pool import ThreadPool
from subprocess import PIPE, STDOUT, Popen
from datetime import datetime

# append root of the python code tree to sys.apth so that imports are working
#   alternative: add path to riotam_backend to the PYTHONPATH environment variable, but this includes one more step
#   which could be forget
CUR_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_DIR = os.path.normpath(os.path.join(CUR_DIR, os.pardir, os.pardir, os.pardir))
sys.path.append(PROJECT_ROOT_DIR)

from riotam_backend.config import config
from BuildTaskStatistic import BuildTaskStatistic
from riotam_backend.common.MyDatabase import MyDatabase

LOGFILE = os.path.join(PROJECT_ROOT_DIR, "log", "prepare_all.log")
USING_CACHE = True

db = MyDatabase()
stat = BuildTaskStatistic()

task_list_lock = multiprocessing.Lock()


def main():

    pool_size = multiprocessing.cpu_count()

    print("preparing build tasks...")
    task_list = get_tasks()

    print("got %s tasks" % len(task_list))

    stat.start()

    print("using cache: %s" % str(USING_CACHE))

    print("starting %d workers..." % pool_size)
    pool = ThreadPool(pool_size, build_worker, (task_list,))
    pool.close()
    pool.join()

    stat.stop()
    print(stat)


def build_worker(task_list):
    """
    Execute a given build task

    Parameters
    ----------
    (board, application): tuple
        Tuple containing a board and an application

    """
    while True:

        task = None

        task_list_lock.acquire()
        if len(task_list) > 0:
            task = task_list.pop(0)
        task_list_lock.release()

        if task is None:
            # no more tasks left in queue, finish this worker
            return

        board = task[0]
        application = task[1]

        start_time = datetime.now().replace(microsecond=0)

        cmd = ["python", "build_example.py",
               "--application", application,
               "--board", board,
               "--prefetching"]

        if USING_CACHE:
            cmd.append("--caching")

        process = Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=os.path.join(PROJECT_ROOT_DIR, "riotam_backend"))
        output = process.communicate()[0]

        end_time = datetime.now().replace(microsecond=0)
        delta = end_time - start_time

        build_result = ast.literal_eval(output)

        failed = not build_result["success"]

        stat.add_completed_task(delta, failed)

        if failed:
            print("[FAILED]: Build of {0} for {1}".format(application, board))
            print(build_result["cmd_output"])

        else:
            print("[DONE]:   Build of {0} for {1}".format(application, board))


def get_tasks():
    """
    Generate build tasks

    Returns
    -------
    array_like
        List of (board, applications) tuples

    """
    applications = fetch_applications()

    task_list = []
    for application in applications:

        app_dir = application["path"]

        for board in get_supported_boards(app_dir):
            task_list.append((board, str(application["id"])))

    return task_list


def get_supported_boards(app_dir):
    """
    Get all supported boards for an application

    Parameters
    ----------
    app_dir: string
        Path to the application directory

    Returns
    -------
    array_like
        List of board names of supported boards

    """
    # command to get supported devices from .murdock script in RIOT repository within get_supported_boards()
    # 2>/dev/null replaced by stderr=open(os.devnull, 'w')
    dev_null = open(os.devnull, "w")
    process = Popen(["make", "--no-print-directory", "-C", app_dir, "info-boards-supported"], stdout=PIPE, stderr=dev_null)
    output = process.communicate()[0]

    return output.split()


def fetch_boards():
    db.query("SELECT * FROM boards ORDER BY display_name")
    return db.fetchall()


def fetch_applications():
    db.query("SELECT * FROM applications ORDER BY name")
    return db.fetchall()


if __name__ == "__main__":

    logging.basicConfig(filename=LOGFILE, format=config.LOGGING_FORMAT,
                        datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)

    try:
        main()

    except Exception as e:
        logging.error(str(e), exc_info=True)
