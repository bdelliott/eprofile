""" Misc test code to profile. """
import time

from eventlet import greenthread
from eventlet import greenpool


def foo(i):
    bar()
    return i


def bar():
    time.sleep(0.0)  # force a greenthread swap


def multi(n=2):
    n = int(n)

    # Run in multiple greenthreads
    pool = greenpool.GreenPool(n)

    results = []

    for result in pool.imap(foo, range(n)):
        results.append(result)


def fib(n):
    n = int(n)

    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)


def swap():
    t1 = greenthread.spawn(foo, 1)
    t2 = greenthread.spawn(wait)

    t1.wait()
    t2.wait()


def wait():
    time.sleep(0.2)
