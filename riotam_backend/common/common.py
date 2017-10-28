#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
 * Copyright (C) 2017 Hendrik van Essen
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
"""

import errno
import os


def create_directories(path):
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