#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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