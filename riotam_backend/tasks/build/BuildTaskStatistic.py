#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
 * Copyright (C) 2017 Hendrik van Essen
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
"""

import textwrap
from datetime import datetime, timedelta
import thread


def timedelta_to_formatted_string(delta):
    """
    Format timedelta to string like hours:minutes:seconds

    Parameters
    ----------
    delta: timedelta
        timedelta to format

    Returns
    -------
    string
        Formatted string

    """
    total_seconds = delta.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "%d:%02d:%02d" % (hours, minutes, seconds)


def average_timedelta(deltas):
    """
    Calculate average of list of timedelta

    Parameters
    ----------
    deltas: array_like
        List of timedelta

    Returns
    -------
    timedelta
        Average timedelta

    """
    if len(deltas) == 0:
        return 0
    
    # start sum with "empty" timedelta instead of 0 as integer
    time_sum = sum(deltas, timedelta(0))

    return time_sum // len(deltas)


class BuildTaskStatistic(object):
    """
    Class to get some statistic about time and amount of tasks

    Methods
    -------
    start()
        Start time measurement
    stop()
        Stop time measurement
    add_completed_task(execute_time, failed=False)
        Add a completed task to update internal values

    """
    _start_time = None
    _end_time = None

    _build_count = 0
    _build_fail_count = 0

    _current_min_execute_time = timedelta.max
    _current_max_execute_time = timedelta.min

    _build_times = []
    _failed_build_times = []

    _active = False
    _finished = False
    _lock = thread.allocate_lock()

    _average_execute_time = None
    _execute_time_failed_builds = None

    def start(self):
        """
        Start time measurement

        """

        if not self._finished and not self._active:
            self._start_time = datetime.now().replace(microsecond=0)
            self._active = True

    def stop(self):
        """
        Stop time measurement

        """

        if self._active and not self._finished:
            self._end_time = datetime.now().replace(microsecond=0)

            self._active = False
            self._finished = True

    def add_completed_task(self, execute_time, failed=False):
        """
        Add a completed task to update internal values

        Parameters
        ----------
        execute_time: timedelta
            Elapsed time in form of timedelta

        failed: bool (default =False)
            Set true if task failed

        """
        self._lock.acquire()

        self._build_count += 1
        if failed:
            self._build_fail_count += 1
            self._failed_build_times.append(execute_time)

        else:
            # only count valid build times
            self._current_min_execute_time = min(self._current_min_execute_time, execute_time)
            self._current_max_execute_time = max(self._current_max_execute_time, execute_time)
            self._build_times.append(execute_time)

        self._lock.release()

    def _update_variables(self):
        """
        Recalculate internal values

        """

        self._average_execute_time = average_timedelta(self._build_times)

        self._execute_time_failed_builds = sum(self._failed_build_times, timedelta(0))

    def __str__(self):

        self._update_variables()

        if not self._active and not self._finished:
            return "%s not initialized yet" % self.__class__.__name__

        elif self._active and not self._finished:

            delta = datetime.now().replace(microsecond=0) - self._start_time
            elapsed_time_string = timedelta_to_formatted_string(delta)

            return textwrap.dedent("""
                ################STATISTICS################
                task
                    running since: {0}
                    elapsed time:  {1}
                    
                build times
                    min build time:     {2}
                    max build time:     {3}
                    average build time: {4}
                    sum failed builds:  {5} (sum of threads by multithreading!)
                    
                build count
                    total builds:  {6}
                    failed builds: {7}
                ##########################################
                """.format(datetime.strftime(self._start_time, "%Y-%m-%d %H:%M:%S"),
                           elapsed_time_string,
                           timedelta_to_formatted_string(self._current_min_execute_time),
                           timedelta_to_formatted_string(self._current_max_execute_time),
                           timedelta_to_formatted_string(self._average_execute_time),
                           timedelta_to_formatted_string(self._execute_time_failed_builds),
                           self._build_count,
                           self._build_fail_count))

        elif self._finished:

            delta = self._end_time - self._start_time
            elapsed_time_string = timedelta_to_formatted_string(delta)

            return textwrap.dedent("""
                ################STATISTICS################
                task
                    started at:   {0}
                    finished at:  {1}
                    elapsed time: {2}
                    
                build times
                    min build time:     {3}
                    max build time:     {4}
                    average build time: {5}
                    sum failed builds:  {6} (sum of threads by multithreading!)
                    
                build count
                    total builds:  {7}
                    failed builds: {8}
                ##########################################
                """.format(datetime.strftime(self._start_time, "%Y-%m-%d %H:%M:%S"),
                           datetime.strftime(self._end_time, "%Y-%m-%d %H:%M:%S"),
                           elapsed_time_string,
                           timedelta_to_formatted_string(self._current_min_execute_time),
                           timedelta_to_formatted_string(self._current_max_execute_time),
                           timedelta_to_formatted_string(self._average_execute_time),
                           timedelta_to_formatted_string(self._execute_time_failed_builds),
                           self._build_count,
                           self._build_fail_count))
