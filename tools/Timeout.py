#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
创建线程装饰器实现函数强制超时
用法：
from Timeout import  timeout
@timeout
def main():
	pass
'''
__all__ = ['timeout']

import ctypes
import functools
import threading


def _async_raise(tid, exception):
    ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(exception))
    if ret == 0:
        raise ValueError('Invalid thread id')
    elif ret != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), 0)
        raise SystemError('PyThreadState_SetAsyncExc failed')


class ThreadTimeout(Exception):
    """ Thread Timeout Exception """
    pass


class WorkThread(threading.Thread):
    """ WorkThread """

    def __init__(self, target, args, kwargs):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.start()

    def run(self):
        try:
            self.result = self.target(*self.args, **self.kwargs)
        except Exception as e:
            self.exception = e
        else:
            self.exception = None

    def get_tid(self):
        if self.ident is None:
            raise threading.ThreadError('The thread is not active')
        return self.ident

    def raise_exc(self, exception):
        _async_raise(self.get_tid(), exception)

    def terminate(self):
        self.raise_exc(SystemExit)


def timeout(timeout):
    """ timeout decorator """
    def proxy(method):
        @functools.wraps(method)
        def func(*args, **kwargs):
            worker = WorkThread(method, args, kwargs)
            worker.join(timeout=timeout)
            if worker.is_alive():
                worker.terminate()
                raise ThreadTimeout('A call to %s() has timed out' % method.__name__)
            elif worker.exception is not None:
                raise worker.exception
            else:
                return worker.result
        return func
    return proxy
