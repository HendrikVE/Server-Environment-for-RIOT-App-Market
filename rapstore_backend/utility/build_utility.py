#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
 * Copyright (C) 2017 Hendrik van Essen
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
"""

import base64
import errno
import glob
import logging
import os
import tarfile
import time
import uuid
from shutil import copytree, rmtree, copyfile
from subprocess import Popen, PIPE, STDOUT


def generate_stripped_repo(app_build_dir, stripped_riot_dir, temp_dir, board, app_name):
    """
    Create stripped version of the riot repository and return the path to it

    Parameters
    ----------
    app_build_dir: string
        Directory to take application data from
    stripped_riot_dir: string
        Directory in which the bare stripped RIOT repository is stored
    temp_dir: string
        Path to temporary directory of the requested application
    board: string
        Name of the Board
    app_name: string
        Name of the application

    Returns
    -------
    string
        Path to the generated stripped RIOT repository

    """
    # TODO Adapt this to get 'files' as parameter, not from disk

    bin_dir = os.path.join(app_build_dir, "bin", board)

    app_copy_dir = os.path.join(temp_dir, "RIOT_stripped", "generated_by_rapstore", app_name)
    bin_copy_dir = os.path.join(app_copy_dir, "bin", board)


    path_stripped_riot = os.path.join(stripped_riot_dir, "RIOT_stripped")
    stripped_repo_path = os.path.join(temp_dir, "RIOT_stripped")

    # Create stripped repository wit firmwares
    _create_riot_flasher(path_stripped_riot, stripped_repo_path,
                         board=board)
    # Mandatory files
    _copy_file_with_parents(os.path.join(app_build_dir, "Makefile"),
                            os.path.join(app_copy_dir, "Makefile"))
    _copy_file_with_parents(app_outfile_path(bin_dir, app_name, 'elf'),
                            app_outfile_path(bin_copy_dir, app_name, 'elf'))
    # Optional files
    optfiles = ('bin', 'hex')
    for optfile in optfiles:
        src = app_outfile_path(bin_dir, app_name, optfile)
        dst = app_outfile_path(bin_copy_dir, app_name, optfile)
        _copy_file_with_parents(src, dst, ignore_no_src=True)

    return stripped_repo_path


def zip_repo(src_path, dest_path):
    """
    Create tar archive of given path and write tar-file to destination

    Parameters
    ----------
    src_path: string
        Source path
    dest_path: string
        Destination path

    """
    try:
        tar = tarfile.open(dest_path, "w:gz")
        for file_name in glob.glob(os.path.join(src_path, "*")):
            tar.add(file_name, os.path.basename(file_name))

        tar.close()

    except Exception as e:
        raise e


def file_as_base64(path):
    """
    Get file content encoded in base64

    Parameters
    ----------
    path: string
        Path to file to be encoded

    Returns
    -------
    string
        Base64 representation of the file

    """
    with open(path, "rb") as file:
        return base64.b64encode(file.read())


def get_ticket_id():
    """Return a generated unique id

    """
    return str(time.time()) + str(uuid.uuid4())


def get_temporary_directory(path, ticket_id):
    """
    Return path to a temporary directory depending on an unique id

    Parameters
    ----------
    path: string
        Path in which the temporary directory should be
    ticket_id: string
        Unique id

    Returns
    -------
    string
        Path to temporary directory

    """
    return os.path.join(path, "tmp", ticket_id)


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
            logging.error(str(e))
            raise


def app_outfile_path(path, app_name, extension):
    """Application outfile path with extension."""
    filename = '%s.%s' % (app_name, extension)
    return os.path.join(path, filename)


def execute_makefile(app_build_dir, board, app_name):
    """
    Run make on given makefile and override variables

    Parameters
    ----------
    app_build_dir: string
        Path to makefile
    board: string
        Board name
    app_name: string
        Application name

    Returns
    -------
    string
        Output from executing make

    """

    # set ELFFILE the same way as RIOT Makefile.include (path to .hex file is extracted from this information)
    app_build_dir_abs_path = os.path.abspath(app_build_dir)

    bindirbase = get_bindirbase(app_build_dir_abs_path)
    bindir = get_bindir(app_build_dir_abs_path, board)
    elffile = app_outfile_path(bindir, app_name, 'elf')

    cmd = ["make",
           "-C", app_build_dir, # work within app_build_dir
           "BOARD=%s" % board,
           "BINDIRBASE=%s" % bindirbase,
           "ELFFILE=%s" % elffile]
    logging.debug('make: %s', cmd)

    process = Popen(cmd, stdout=PIPE, stderr=STDOUT)
    return process.communicate()[0]


def get_bindirbase(app_build_dir):
    return os.path.abspath(os.path.join(app_build_dir, "bin"))


def get_bindir(app_build_dir, board):

    app_build_dir = os.path.abspath(app_build_dir)

    bin_dir_base = get_bindirbase(app_build_dir)
    bin_dir = os.path.join(bin_dir_base, board)

    return bin_dir


def _copy_file_with_parents(src, dst, ignore_no_src=False):
    """Copy `src` to `dst` and create `dst` parents directories.

    If `src` does not exist and `ignore_no_src` is set, do nothing.
    """
    if not os.path.isfile(src) and ignore_no_src:
        return

    dst_dir = os.path.dirname(dst)
    create_directories(dst_dir)

    copyfile(src, dst)


def _create_riot_flasher(src_path, dest_path, board=None):
    """Create a minimal RIOT repository to allow flashing.

    If `board` is set, remove unused boards

    Parameters
    ----------
    src_path: string
        Path to riot repository you want to be stripped
    dest_path: string
        Path to store the stripped riot repository
    board: string
        Name of the board
    """
    copytree(src_path, dest_path)
    if board:
        _flasher_remove_unnecessary_boards(dest_path, board)


def _flasher_remove_unnecessary_boards(dest_path, board):
    """Remove all unnecessary boards from `boards` directory."""
    boards_dir = os.path.join(dest_path, 'boards')
    for entry in os.listdir(boards_dir):
        entry_path = os.path.join(boards_dir, entry)
        if os.path.isfile(entry_path):
            continue
        if (entry in ('include', board)) or ('common' in entry):
            continue

        try:
            rmtree(entry_path)
        except Exception as e:
            logging.error(str(e), exc_info=True)
