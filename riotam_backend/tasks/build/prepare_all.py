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
    tasks = get_build_tasks()

    stat.start()

    execute_tasks(thread_count, tasks)

    stat.stop()
    print(stat)


def execute_tasks(thread_count, tasks):

    pool = ThreadPool(thread_count)
    results = pool.map(execute_build, tasks[:4])
    pool.close()
    pool.join()


def execute_build((board, application)):

    cmd = ["python", "build_example.py",
           "--application", application,
           "--board", board]

    process = Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=os.path.join(PROJECT_ROOT_DIR, "riotam_backend"))
    output = process.communicate()[0]

    build_result = ast.literal_eval(output)

    failed = build_result["success"]

    stat.add_completed_task(failed)
    if failed:
        print("[FAILED]: Build of {0} for {1}".format(application, board))

    else:
        print("[DONE]:   Build of {0} for {1}".format(application, board))


def get_build_tasks():

    boards = fetch_boards()
    applications = fetch_applications()

    build_tasks = []
    for board in boards:
        for application in applications:
            build_tasks.append((board["internal_name"], str(application["id"])))

    return build_tasks


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
