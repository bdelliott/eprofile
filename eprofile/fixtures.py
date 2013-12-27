""" Misc test code to profile. """
import time

from eventlet import greenpool


def foo(i):
    bar()
    return i


def bar():
    time.sleep(0.1)  # force a greenthread swap


def multi():
    # Run in multiple greenthreads
    pool = greenpool.GreenPool(2)

    results = []

    for result in pool.imap(foo, range(2)):
        results.append(result)


def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)
