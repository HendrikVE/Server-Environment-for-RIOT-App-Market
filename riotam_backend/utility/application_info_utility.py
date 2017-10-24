#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os


def get_used_modules(db, app_id):
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
                modules.append(line[index_begin + 1:])

    return modules
