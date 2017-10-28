#! /usr/bin/env python
# -*- coding:utf-8 -*-

"""
 * Copyright (C) 2017 Hendrik van Essen
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
"""

"""Create backend database and repository.

"""

from __future__ import division, print_function, unicode_literals

import MySQLdb
from getpass import getpass

import db_config as config


def main():

    if config.db_config["user_privileged"] == "USER_PRIVILEGED":
        privileged_user = raw_input("Please enter name of privileged database user: ")
        privileged_password = getpass()

    else:
        privileged_user = config.db_config["user_privileged"]
        privileged_password = config.db_config["passwd_privileged"]

    db = MySQLdb.connect(user=privileged_user, passwd=privileged_password)
    db_cursor = db.cursor()

    host = config.db_config["host"]
    database = config.db_config["db"]

    user_backend = config.db_config["user_backend"]
    password_backend = config.db_config["passwd_backend"]
    granted_backend = "SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER"

    user_website = config.db_config["user_website"]
    password_website = config.db_config["passwd_website"]
    granted_website = "SELECT"

    print("Cleanup database")
    drop_database(db_cursor, database)
    drop_user(db_cursor, user_backend, host)
    drop_user(db_cursor, user_website, host)

    print()

    print("Create database")
    db_cursor.execute("CREATE DATABASE %s;" % database)
    create_user(db_cursor, host, user_backend, password_backend, database, granted_backend)
    create_user(db_cursor, host, user_website, password_website, database, granted_website)

    db_cursor.close()
    db.close()


def create_user(cur, host, user, password, database, granted):

    sql = "CREATE USER '{USER}'@'{HOST}' IDENTIFIED BY '{PASSWORD}';".format(HOST=host, USER=user, PASSWORD=password)
    try:
        print("executed: %s" % sql)
        cur.execute(sql)

    except Exception as e:
        print (str(e))

    sql = "GRANT {GRANTED} ON {DATABASE}.* TO '{USER}'@'{HOST}';".format(GRANTED=granted, DATABASE=database, USER=user, HOST=host)
    try:
        print("executed: %s" % sql)
        cur.execute(sql)

    except Exception as e:
        print(str(e))


def drop_database(cur, database):

    sql = "DROP DATABASE {DATABASE};".format(DATABASE=database)
    try:
        cur.execute(sql)
        print ("executed: %s" % sql)

    except Exception as e:
        print (str(e))


def drop_user(cur, user, host):

    sql = "DROP USER '{USER}'@'{HOST}';".format(USER=user, HOST=host)
    try:
        cur.execute(sql)
        print("executed: %s" % sql)

    except Exception as e:
        print (str(e))


if __name__ == "__main__":

    main()
