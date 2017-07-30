#!/bin/env python
#-*- coding: utf-8 -*-

import signal

def timeout(func, args = (), kwargs = {}, timeout = 0, default = None):
    class TimeoutError(Exception): pass

    def handler(signum, frame): raise TimeoutError()

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)
    try:
        ret = func(*args, **kwargs)
    except TimeoutError as exc:
        ret = default
    finally:
        signal.alarm(0)

    return ret
