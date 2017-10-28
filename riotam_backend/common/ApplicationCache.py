#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
 * Copyright (C) 2017 Hendrik van Essen
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
"""

import os
import sys
from shutil import copytree, copyfile

# append root of the python code tree to sys.apth so that imports are working
#   alternative: add path to riotam_backend to the PYTHONPATH environment variable, but this includes one more step
#   which could be forget
CUR_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_DIR = os.path.normpath(os.path.join(CUR_DIR, os.pardir, os.pardir))
sys.path.append(PROJECT_ROOT_DIR)

from common import create_directories


class ApplicationCache(object):

    _cache_dir = None

    def __init__(self, cache_dir):
        self._cache_dir = cache_dir

    def get_entry(self, board, app_name, file_name):

        cache_path = os.path.join(self._cache_dir, board, app_name)

        result_file_path = os.path.join(cache_path, file_name)
        ready_to_use_file = os.path.join(cache_path, ".ready_to_use")

        if not os.path.isfile(result_file_path):
            return None

        if os.path.isfile(ready_to_use_file):
            return result_file_path

        else:
            return None

    def cache(self, path, board, app_name, file_name):

        create_directories(self._cache_dir)

        # only store if not in cache already
        if self.get_entry(board, app_name, file_name) is None:

            dest_in_cache = os.path.join(self._cache_dir, board, app_name)

            create_directories(dest_in_cache)
            copyfile(path, os.path.join(dest_in_cache, file_name))

            # show that cached application/module is now ready to use
            ready_file_path = os.path.join(dest_in_cache, ".ready_to_use")
            open(ready_file_path, "a").close()
