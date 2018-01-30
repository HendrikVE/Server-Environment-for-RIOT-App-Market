#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
 * Copyright (C) 2017 Hendrik van Essen
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
"""

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