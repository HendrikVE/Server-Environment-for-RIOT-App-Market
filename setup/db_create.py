#! /usr/bin/env python
# -*- coding:utf-8 -*-

"""Create backend database and repository.

It should be run as the root account without mysql password.
"""

from __future__ import division, print_function, unicode_literals

import MySQLdb
import argparse
import sys

import db_config as config


def main(argv):

    parser = init_argparse()

    try:
        args = parser.parse_args(argv)

    except Exception as e:
        print (str(e))
        return

    privileged_user = args.user
    privileged_password = args.password

    if privileged_user is None or privileged_password is None:

        if privileged_password is None and privileged_user is not None:
            db = MySQLdb.connect(user=privileged_user)
        else:
            db = MySQLdb.connect()

    else:
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


def init_argparse():

    parser = argparse.ArgumentParser(description="Create database for riotam")

    parser.add_argument("--user",
                        dest="user", action="store",
                        required=False,
                        help="privileged database user")

    parser.add_argument("--password",
                        dest="password", action="store",
                        required=False,
                        help="password for user")

    return parser


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

    main(sys.argv[1:])
