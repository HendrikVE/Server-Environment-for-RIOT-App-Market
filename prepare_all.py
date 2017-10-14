#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function

import ast
import json
import logging
import multiprocessing
import os
from multiprocessing.pool import ThreadPool
from subprocess import PIPE, STDOUT, Popen

from BuildTaskStatistic import BuildTaskStatistic
from MyDatabase import MyDatabase

CURDIR = os.path.dirname(__file__)
LOGFILE = os.path.join(CURDIR, "log/prepare_all_log.txt")

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

    process = Popen(cmd, stdout=PIPE, stderr=STDOUT)
    output = process.communicate()[0]

    build_result = ast.literal_eval(output)

    failed = build_result["success"]

    stat.add_completed_task(failed)
    if failed:
        print("[FAILED]: Build of {0} for {1}".format(application, board))

    else:
        print("[DONE]: Build of {0} for {1}".format(application, board))


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
