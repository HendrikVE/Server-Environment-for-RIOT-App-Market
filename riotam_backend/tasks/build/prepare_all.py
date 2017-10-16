#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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
PROJECT_ROOT_DIR = os.path.normpath(os.path.join(CUR_DIR, "..", "..", ".."))
sys.path.append(PROJECT_ROOT_DIR)

from BuildTaskStatistic import BuildTaskStatistic
from riotam_backend.common.MyDatabase import MyDatabase

LOGFILE = os.path.join(PROJECT_ROOT_DIR, "log", "prepare_all_log.txt")

db = MyDatabase()
stat = BuildTaskStatistic()


def main():

    thread_count = multiprocessing.cpu_count()

    print("preparing build tasks...")
    tasks = get_build_tasks()

    print("got %s tasks" % len(tasks))

    stat.start()

    print("starting worker threads...")
    execute_tasks(thread_count, tasks)

    stat.stop()
    print(stat)


def execute_tasks(thread_count, tasks):
    """
    Execute given tasks by threadpool

    Parameters
    ----------
    thread_count: int
        Amount of threads to be used within threadpool

    tasks: array_like
        List of (board, applications) tuples

    """
    pool = ThreadPool(thread_count)
    results = pool.map(execute_build, tasks)
    pool.close()
    pool.join()


def execute_build((board, application)):
    """
    Execute a given build task

    Parameters
    ----------
    (board, application): tuple
        Tuple containing a board and an application

    """
    start_time = datetime.now().replace(microsecond=0)

    cmd = ["python", "build_example.py",
           "--application", application,
           "--board", board]

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


def get_build_tasks():
    """
    Generate build tasks

    Returns
    -------
    array_like
        List of (board, applications) tuples

    """
    applications = fetch_applications()

    build_tasks = []
    for application in applications:

        app_dir = application["path"]

        for board in get_supported_boards(app_dir):
            build_tasks.append((board, str(application["id"])))

    return build_tasks


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

    logging.basicConfig(filename=LOGFILE, format="%(asctime)s [%(levelname)s]: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)

    try:
        main()

    except Exception as e:
        logging.error(str(e), exc_info=True)
