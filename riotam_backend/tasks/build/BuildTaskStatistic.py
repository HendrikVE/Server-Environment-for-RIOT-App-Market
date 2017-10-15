#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import textwrap
from datetime import datetime


def timedelta_to_formatted_string(delta):

    total_seconds = delta.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "%d:%02d:%02d" % (hours, minutes, seconds)


class BuildTaskStatistic(object):

    _start_time = 0
    _end_time = 0
    _build_count = 0
    _build_fail_count = 0

    _active = False
    _finished = False

    def start(self):

        if not self._finished and not self._active:
            self._start_time = datetime.now().replace(microsecond=0)
            self._active = True

    def stop(self):

        if self._active and not self._finished:
            self._end_time = datetime.now().replace(microsecond=0)

            self._active = False
            self._finished = True

    def add_completed_task(self, failed=False):

        self._build_count += 1
        if failed:
            self._build_fail_count += 1

    def __str__(self):

        if not self._active and not self._finished:
            return "%s not initialized yet" % self.__class__.__name__

        elif self._active and not self._finished:
            delta = datetime.now().replace(microsecond=0) - self._start_time
            elapsed_time_string = timedelta_to_formatted_string(delta)
            return textwrap.dedent("""
                ################STATISTICS################
                running since: {0}
                 elapsed time: {1}
                 total builds: {2}
                failed builds: {3}
                ##########################################
                """.format(datetime.strftime(self._start_time, "%Y-%m-%d %H:%M:%S"),
                           elapsed_time_string,
                           self._build_count,
                           self._build_fail_count))

        elif self._finished:
            delta = self._end_time - self._start_time
            elapsed_time_string = timedelta_to_formatted_string(delta)
            return textwrap.dedent("""
                ################STATISTICS################
                   started at: {0}
                  finished at: {1}
                 elapsed time: {2}
                 total builds: {3}
                failed builds: {4}
                ##########################################
                """.format(datetime.strftime(self._start_time, "%Y-%m-%d %H:%M:%S"),
                           datetime.strftime(self._end_time, "%Y-%m-%d %H:%M:%S"),
                           elapsed_time_string,
                           self._build_count,
                           self._build_fail_count))
