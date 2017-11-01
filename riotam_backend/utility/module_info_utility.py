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


def get_module_path(db, module_id):

    db.query("SELECT path FROM modules WHERE id=%s", (module_id,))
    applications = db.fetchall()

    logging.debug("asked for %s" % module_id)
    logging.debug("got %s" % str(applications))

    if len(applications) != 1:
        logging.error("error in database: len(applications != 1)")
        return None

    else:
        return applications[0]["path"]


def get_module_name(db, module_id):

    db.query("SELECT name FROM modules WHERE id=%s", (module_id,))
    applications = db.fetchall()

    if len(applications) != 1:
        logging.error("error in database: len(applications != 1)")
        return None

    else:
        return applications[0]["name"]


def get_module_id(db, module_name):

    db.query("SELECT id FROM modules WHERE name=%s", (module_name,))
    applications = db.fetchall()

    logging.debug("asked for %s" % module_name)
    logging.debug("got %s" % str(applications))

    if len(applications) != 1:
        logging.error("error in database: len(applications != 1)")
        return None

    else:
        return int(applications[0]["id"])
