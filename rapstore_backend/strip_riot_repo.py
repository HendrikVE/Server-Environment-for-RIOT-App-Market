#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
 * Copyright (C) 2017 Hendrik van Essen
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
"""

from __future__ import print_function

import os
import sys
from shutil import copytree, rmtree, copyfile

# append root of the python code tree to sys.apth so that imports are working
#   alternative: add path to rapstore_backend to the PYTHONPATH environment variable, but this includes one more step
#   which could be forget
CUR_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_DIR = os.path.normpath(os.path.join(CUR_DIR, os.pardir))
sys.path.append(PROJECT_ROOT_DIR)

from rapstore_backend.config import strip_config as config


def main():

    path_riot = os.path.join(PROJECT_ROOT_DIR, "RIOT")
    path_riot_stripped = os.path.join(PROJECT_ROOT_DIR, "RIOT_stripped")
    
    try:
        if os.path.exists(path_riot_stripped):
            rmtree(path_riot_stripped)
            
        copytree(path_riot, path_riot_stripped, ignore=config.ignore_patterns)
        
        path = os.path.join(path_riot_stripped, "Makefile.include")
        # Save the old one to check later in case there is an error
        copyfile(path, path + '.old')

        with open(path + '.old', "r") as old_makefile:
            with open(path, "w") as makefile:
                for line in old_makefile.readlines():

                    if line.startswith("flash: all") or line.startswith("preflash: all"):
                        print('Changing lines:')
                        print('    %s' % line)
                        line = line.replace(" all", "")
                        print(' -> %s' % line)

                    makefile.write(line)

    except Exception as e:
        print (e)
        exit(1)


if __name__ == "__main__":

    main()
