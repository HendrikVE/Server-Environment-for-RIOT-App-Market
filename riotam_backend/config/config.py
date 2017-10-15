#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os

db_config = {
    "host": "localhost",
    "user": "riotam_backend",
    "passwd": "Ny417Yk75zbrCcE7Sy3A",
    "db": "riot_os"
}

_CUR_DIR = os.path.abspath(os.path.dirname(__file__))
_PROJECT_ROOT_DIR = os.path.normpath(os.path.join(_CUR_DIR, "..", ".."))

path_root = os.path.join(_PROJECT_ROOT_DIR, "RIOT")

module_directories = [
    "sys",
    "pkg",
    "drivers",
    "tests"
]

application_directories = [
    "examples"
]