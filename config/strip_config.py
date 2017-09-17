#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from shutil import ignore_patterns

ignore_patterns = ignore_patterns(
    ".*",
    "doc",
    "tests",
    "generated_by_riotam",
    "examples"
)