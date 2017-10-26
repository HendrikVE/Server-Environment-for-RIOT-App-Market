#!/usr/bin/env python
# -*- coding: UTF-8 -*-

db_config = {
    "host": "localhost",
    "user": "riotam_backend",
    "passwd": "PASSWORD_BACKEND",
    "db": "riot_os"
}

path_root = "RIOT/"

module_directories = [
    "sys",
    "pkg",
    "drivers"
]

application_directories = [
    "examples"
]

LOGGING_FORMAT = "[%(levelname)s]: %(asctime)s\n"\
                 + "in %(filename)s in %(funcName)s on line %(lineno)d\n"\
                 + "%(message)s\n"

MODULE_CACHE_DIR = ".module_cache"
APPLICATION_CACHE_DIR = ".application_cache"
