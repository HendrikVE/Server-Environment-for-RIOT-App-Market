#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import base64
import errno
import glob
import logging
import os
import subprocess
import tarfile
import time
import uuid
from shutil import copytree, rmtree, copyfile


def prepare_stripped_repo(src_path, dest_path, single_copy_operations, board):
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
        dest_path = os.path.join(dest_path, "RIOT_stripped")
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
            copy_dest_path = os.path.join(dest_path, operation[1])
            index = copy_dest_path.rindex("/")
            path_to_create = copy_dest_path[:index]
            create_directories(path_to_create)

            copyfile(operation[0], copy_dest_path)

        return dest_path

    except Exception as e:
        logging.error(str(e), exc_info=True)

    return None


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
    return str(time.time()) + str(uuid.uuid1())


def get_temporary_directory(ticket_id):
    """
    Return path to a temporary directory depending on an unique id

    Parameters
    ----------
    ticket_id: string
        Unique id

    Returns
    -------
    string
        Path to temporary directory

    """
    return os.path.join("tmp", ticket_id)


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


def execute_makefile(path, board):
    """
    Run make on given makefile and override variables

    Parameters
    ----------
    path: string
        Path to makefile
    board: string
        Board name

    Returns
    -------
    string
        Output from executing make

    """
    cmd = ["make", "--directory=%s" % path,
           "BOARD=%s" % board]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return process.communicate()[0]
