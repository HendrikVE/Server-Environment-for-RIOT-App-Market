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


def prepare_stripped_repo(src_path, temporary_directory, single_copy_operations, board):
    try:
        dest_path = temporary_directory + "RIOT_stripped/"
        copytree(src_path, dest_path)

        try:
            # remove all unnecessary boards
            path_boards = dest_path + "boards/"
            for item in os.listdir(path_boards):
                if not os.path.isfile(os.path.join(path_boards, item)):
                    if (item != "include") and (not "common" in item) and (item != board):
                        rmtree(path_boards + item)

        except Exception as e:
            logging.error(str(e), exc_info=True)

        for operation in single_copy_operations:
            # remove file from path, because it shouldnt be created as directory
            copy_dest_path = temporary_directory + operation[1]
            index = copy_dest_path.rindex("/")
            path_to_create = copy_dest_path[:index]
            create_directories(path_to_create)

            copyfile(operation[0], copy_dest_path)

        return dest_path

    except Exception as e:
        logging.error(str(e), exc_info=True)

    return None


def zip_repo(src_path, dest_path):
    try:
        tar = tarfile.open(dest_path, "w:gz")
        for file_name in glob.glob(os.path.join(src_path, "*")):
            tar.add(file_name, os.path.basename(file_name))

        tar.close()

    except Exception as e:
        logging.error(str(e), exc_info=True)

    return dest_path


def file_as_base64(path):
    with open(path, "rb") as file:
        return base64.b64encode(file.read())


def get_ticket_id():
    return str(time.time()) + str(uuid.uuid1())


def get_temporary_directory(ticket_id):
    return "tmp/{!s}/".format(ticket_id)


def create_directories(path):
    try:
        os.makedirs(path)

    except OSError as e:

        if e.errno != errno.EEXIST:
            logging.error(str(e))
            raise


def execute_makefile(path, board):

    cmd = ["make", "--directory=%s" % path,
           "BOARD=%s" % board]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.communicate()[0]
