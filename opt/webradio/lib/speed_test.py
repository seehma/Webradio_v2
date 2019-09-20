#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################
# This script provides a methode for latency-test of a given filenpath,
# how fast can the given filename be accessed (read)
# The function "latenceTest" will be performed with a time-out of 0,04 seconds (40ms) which should be enough for
# Every type of computer with a
# - local stored
# - USB-Stick attached
# - USB-HDD attached
# - fast NAS Connection
# connected file-storage
################################

import time
import multiprocessing
import logging

logger = logging.getLogger(__name__)

class TimeoutException(Exception):
    pass


class RunableProcessing(multiprocessing.Process):
    def __init__(self, func, *args, **kwargs):
        self.queue = multiprocessing.Queue(maxsize=1)
        args = (func,) + args
        multiprocessing.Process.__init__(self, target=self.run_func, args=args, kwargs=kwargs)

    def run_func(self, func, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
            self.queue.put((True, result))
        except Exception as e:
            self.queue.put((False, e))

    def done(self):
        return self.queue.full()

    def result(self):
        return self.queue.get()


def timeout(seconds, force_kill=True):
    def wrapper(function):
        def inner(*args, **kwargs):
            now = time.time()
            proc = RunableProcessing(function, *args, **kwargs)
            proc.start()
            proc.join(seconds)
            if proc.is_alive():
                if force_kill:
                    proc.terminate()
                runtime = float(time.time() - now)
                raise TimeoutException('timed out after {0} seconds'.format(runtime))
            assert proc.done()
            success, result = proc.result()
            if success:
                return result
            else:
                raise result
        return inner
    return wrapper


def timing(f):
    def wrap(*args):
        time1 = time.time()
        f(*args)
        time2 = time.time()
        #print('{0} function took {1:0.3f} ms').format(f.func_name, (time2-time1)*1000.0)
        return round((time2-time1)*1000.0, 3)
    return wrap

@timeout(0.04, force_kill=True)    #40ms for 30 lines is the limit
@timing
def latencyTest(filepath):
    """
    Test the latency of a given Filepath
    timing-wrapper: Will return the needed time to read 30 lines of the file in ms (milli-seconds)
    timeout-wrapper: Will kill the function and raise a "TimeException" -> To this, you should react.
    :param filepath: Absolute Filepath to existing file to which the latency should be probed
    :return:
    """
    with open(filepath, 'r') as file:
        file.readline(30)



if __name__ == "__main__":
    pathlist = []
    testpath_1 = "/home/matthias/Musik/Fall.mp3"
    testpath_2 = "/media/server/server_music/Musik2/08_Drive.mp3"

    pathlist.append(testpath_1)
    pathlist.append(testpath_2)

    for path in pathlist:
        print(latencyTest(path))
