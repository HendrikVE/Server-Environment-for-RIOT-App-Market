#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
 * Copyright (C) 2017 Hendrik van Essen
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
"""


def get_build_result_template():

    build_result = {
        'cmd_output': '',
        'board': None,
        'application_name': 'application',
        'output_archive': None,
        'success': False
    }

    return build_result
