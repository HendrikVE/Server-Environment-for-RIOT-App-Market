#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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
    bin_dir = os.path.join(app_build_dir, "bin", board)
    elffile_path = app_elffile_path(bin_dir, app_name)
    hexfile_path = app_hexfile_path(bin_dir, app_name)

    app_copy_dir = os.path.join(temp_dir, "RIOT_stripped", "generated_by_riotam", app_name)
    bin_copy_dir = os.path.join(app_copy_dir, "bin", board)

    elffile_dest_path = app_elffile_path(bin_copy_dir, app_name)
    hexfile_dest_path = app_hexfile_path(bin_copy_dir, app_name)
    makefile_dest_path = app_copy_dir

    # [(src_path, dest_path)]
    single_copy_operations = [
        (elffile_path, elffile_dest_path),
        (hexfile_path, hexfile_dest_path),
        (os.path.join(app_build_dir, "Makefile"), os.path.join(makefile_dest_path, "Makefile"))
    ]

    path_stripped_riot = os.path.join(stripped_riot_dir, "RIOT_stripped")
    stripped_repo_path = _prepare_stripped_repo(path_stripped_riot, os.path.join(temp_dir, "RIOT_stripped"),
                                                  single_copy_operations, board)

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
        logging.error(str(e), exc_info=True)


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


def app_elffile_path(path, app_name):
    return os.path.join(path, "%s.elf" % app_name)


def app_hexfile_path(path, app_name):
    elffile_path = app_elffile_path(path, app_name)
    return _rreplace(elffile_path, ".elf", ".hex", 1)


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
    elffile = app_elffile_path(bindir, app_name)

    cmd = ["make", "--directory=%s" % app_build_dir,
           "BOARD=%s" % board,
           "BINDIRBASE=%s" % bindirbase,
           "ELFFILE=%s" % elffile]

    process = Popen(cmd, stdout=PIPE, stderr=STDOUT)
    return process.communicate()[0]


def get_bindirbase(app_build_dir):
    return os.path.abspath(os.path.join(app_build_dir, "bin"))


def get_bindir(app_build_dir, board):

    app_build_dir = os.path.abspath(app_build_dir)

    bindirbase = get_bindirbase(app_build_dir)
    bindir = os.path.join(bindirbase, board)

    return bindir


def _prepare_stripped_repo(src_path, dest_path, single_copy_operations, board):
    """
    Strip a RIOT repositiory to a minimal version, so that flashing still works

    Parameters
    ----------
    src_path: string
        Path to riot repository you want to be stripped
    dest_path: string
        Path to store the stripped riot repository
    single_copy_operations: array_like
        List of (src_path, dest_path) tuples to copy files
    board: string
        Name of the board

    Returns
    -------
    string
        Path to stripped RIOT repository

    """
    try:
        copytree(src_path, dest_path)

        try:
            # remove all unnecessary boards
            path_boards = os.path.join(dest_path, "boards")
            for item in os.listdir(path_boards):
                if not os.path.isfile(os.path.join(path_boards, item)):
                    if (item != "include") and (not "common" in item) and (item != board):
                        rmtree(os.path.join(path_boards, item))

        except Exception as e:
            logging.error(str(e), exc_info=True)

        for operation in single_copy_operations:
            # remove file from path, because it shouldnt be created as directory
            copy_dest_path = operation[1]
            index = copy_dest_path.rindex("/")
            path_to_create = copy_dest_path[:index]
            create_directories(path_to_create)

            try:
                copyfile(operation[0], copy_dest_path)

            except Exception as e:
                logging.debug(str(e))

        return dest_path

    except Exception as e:
        logging.error(str(e), exc_info=True)

    return None


def _rreplace(string, old, new, occurrences):
    list = string.rsplit(old, occurrences)
    return new.join(list)
