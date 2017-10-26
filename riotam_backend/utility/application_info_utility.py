#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import os


def get_defined_modules(db, app_id):

    application_path = get_application_path(db, app_id)

    return get_modules_from_makefile(application_path)


def get_modules_from_makefile(path_to_makefile):
    modules = []

    path_to_makefile = os.path.join(path_to_makefile, "Makefile")

    with open(path_to_makefile) as make_file:

        for line in make_file:

            line = line.strip()
            if line.startswith("USEMODULE"):
                index_begin = line.rfind(" ")
                modules.append(line[index_begin + 1:])

    return modules


"""
def get_used_modules(db, bindir):

    directories = filter(os.path.isdir, os.listdir(bindir))

    return [dir for dir in directories if is_cacheable_module(db, dir)]


def is_cacheable_module(db, module_name):

    db.query("SELECT * FROM modules where name='%s'" % module_name)
    modules = db.fetchall()

    return len(modules) == 1
"""


def get_application_path(db, app_id):

    db.query("SELECT path FROM applications WHERE id=%s", (app_id,))
    applications = db.fetchall()

    if len(applications) != 1:
        logging.error("error in database: len(applications != 1)")
        return None

    else:
        return applications[0]["path"]


def get_application_name(db, app_id):

    db.query("SELECT name FROM applications WHERE id=%s", (app_id,))
    applications = db.fetchall()

    if len(applications) != 1:
        logging.error("error in database: len(applications != 1)")
        return None

    else:
        return applications[0]["name"]