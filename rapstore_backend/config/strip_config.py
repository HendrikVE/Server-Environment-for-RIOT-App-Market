#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
 * Copyright (C) 2017 Hendrik van Essen
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
"""

from shutil import ignore_patterns

ignore_patterns = ignore_patterns(
    ".*",
    "doc",
    "tests",
    "generated_by_rapstore",
    "examples"
)
