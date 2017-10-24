#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

# append root of the python code tree to sys.apth so that imports are working
#   alternative: add path to riotam_backend to the PYTHONPATH environment variable, but this includes one more step
#   which could be forget
from shutil import copytree

import errno

CUR_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_DIR = os.path.normpath(os.path.join(CUR_DIR, "..", ".."))
sys.path.append(PROJECT_ROOT_DIR)

import riotam_backend.utility.build_utility as b_util


def _create_directories(path):
    """
    Creates all directories on path

    Parameters
    ----------
    path: string
        Path to create

    Raises
    -------
    OSError
        Something fails creating directories, except errno is EEXIST

    """
    try:
        os.makedirs(path)

    except OSError as e:

        if e.errno != errno.EEXIST:
            raise


class ModuleCache(object):

    _cache_dir = None

    def __init__(self, cache_dir):
        self._cache_dir = cache_dir

    def __del__(self):
        pass

    def get_cache_entry(self, board, module_name):
        cache_path = os.path.join(self._cache_dir, board, module_name)
        ready_to_use_file = os.path.join(cache_path, ".ready_to_use")

        if os.path.isfile(ready_to_use_file):
            return cache_path

        else:
            return None

    def cache_module(self, app_build_dir, board, module_name):

        _create_directories(self._cache_dir)

        # only store if not in cache already
        if self.get_cache_entry(board, module_name) is None:
            app_build_dir_abs_path = os.path.abspath(app_build_dir)
            bindir = b_util.get_bindir(app_build_dir_abs_path, board)

            module_path = os.path.join(bindir, module_name)
            dest_in_cache = os.path.join(self._cache_dir, board, module_name)

            copytree(module_path, dest_in_cache)

            # show that cached module is now ready to use
            ready_file_path = os.path.join(dest_in_cache, ".ready_to_use")
            open(ready_file_path, "a").close()

