#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import textwrap
from datetime import datetime, timedelta
import thread


def timedelta_to_formatted_string(delta):

    total_seconds = delta.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "%d:%02d:%02d" % (hours, minutes, seconds)


def average_timedelta(deltas):

    # start sum with "empty" timedelta instead of 0 as integer
    time_sum = sum(deltas, timedelta(0))

    return time_sum // len(deltas)


class BuildTaskStatistic(object):

    _start_time = None
    _end_time = None

    _build_count = 0
    _build_fail_count = 0

    _current_min_execute_time = timedelta.max
    _current_max_execute_time = timedelta.min
    _execute_times = []

    _active = False
    _finished = False
    _lock = thread.allocate_lock()

    def start(self):

        if not self._finished and not self._active:
            self._start_time = datetime.now().replace(microsecond=0)
            self._active = True

    def stop(self):

        if self._active and not self._finished:
            self._end_time = datetime.now().replace(microsecond=0)

            self._active = False
            self._finished = True

    def add_completed_task(self, execute_time, failed=False):

        self._lock.acquire()

        print(execute_time)

        self._build_count += 1
        if failed:
            self._build_fail_count += 1

        else:
            # only count valid build times
            self._current_min_execute_time = min(self._current_min_execute_time, execute_time)
            self._current_max_execute_time = max(self._current_max_execute_time, execute_time)
            self._execute_times.append(execute_time)

        self._lock.release()

    def __str__(self):

        if not self._active and not self._finished:
            return "%s not initialized yet" % self.__class__.__name__

        elif self._active and not self._finished:
            delta = datetime.now().replace(microsecond=0) - self._start_time
            elapsed_time_string = timedelta_to_formatted_string(delta)

            average_execute_time = average_timedelta(self._execute_times)
            return textwrap.dedent("""
                ################STATISTICS################
                     running since: {0}
                      elapsed time: {1}
                    min build time: {2}
                    max build time: {3}
                average build time: {4}
                      total builds: {5}
                     failed builds: {6}
                ##########################################
                """.format(datetime.strftime(self._start_time, "%Y-%m-%d %H:%M:%S"),
                           elapsed_time_string,
                           timedelta_to_formatted_string(self._current_min_execute_time),
                           timedelta_to_formatted_string(self._current_max_execute_time),
                           timedelta_to_formatted_string(average_execute_time),
                           self._build_count,
                           self._build_fail_count))

        elif self._finished:
            delta = self._end_time - self._start_time
            elapsed_time_string = timedelta_to_formatted_string(delta)

            average_execute_time = average_timedelta(self._execute_times)
            return textwrap.dedent("""
                ################STATISTICS################
                        started at: {0}
                       finished at: {1}
                    min build time: {2}
                    max build time: {3}
                average build time: {4}
                      elapsed time: {5}
                      total builds: {6}
                     failed builds: {7}
                ##########################################
                """.format(datetime.strftime(self._start_time, "%Y-%m-%d %H:%M:%S"),
                           datetime.strftime(self._end_time, "%Y-%m-%d %H:%M:%S"),
                           timedelta_to_formatted_string(self._current_min_execute_time),
                           timedelta_to_formatted_string(self._current_max_execute_time),
                           timedelta_to_formatted_string(average_execute_time),
                           elapsed_time_string,
                           self._build_count,
                           self._build_fail_count))
