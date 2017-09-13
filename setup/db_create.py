#! /usr/bin/env python
# -*- coding:utf-8 -*-

"""Create backend database and repository.

It should be run as the root account without mysql password.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import MySQLdb as db
import db_config as config


REMOVE_DB = (
    "DROP DATABASE {db};\n"
    "DROP USER '{user}'@'{host}';\n"
)
REMOVE_DB = REMOVE_DB.format(**config.db_config)

WRITE_GRANTS = "SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER"
CREATE_DB = (
    "CREATE DATABASE {db};\n"
    "CREATE USER '{user}'@'{host}' IDENTIFIED BY '{passwd}';\n"
    "GRANT {write} ON {db}.* TO '{user}'@'{host}';\n"
    "SHOW GRANTS FOR '{user}'@'{host}';\n"
)
CREATE_DB = CREATE_DB.format(write=WRITE_GRANTS, **config.db_config)


def main():
    """Create database and users."""
    conn = db.connect()
    cur = conn.cursor()

    print('Cleanup database')
    for line in REMOVE_DB.splitlines():
        print(line)
        cur.execute(line)
    print()

    print('Create database')
    for line in CREATE_DB.splitlines():
        print(line)
        cur.execute(line)

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
