import base

from eprofile import trace


class SingleThreadTestCase(base.TestCase):

    def test_single(self):
        # test single threaded tracing

        gid = trace._gid()
        trace.enable()
        fib(3)
        bar()
        trace.disable()

        threads = trace.threads
        self.assertEqual(1, len(threads))
        self.assertEqual(gid, threads.keys()[0])

        thread = threads.values()[0]
        # stack should be empty
        print thread.stack
        self.assertEqual(0, len(thread.stack))

        # should be top-level calls made
        self.assertEqual(2, len(thread.calls))

        # first call is to fib(3)
        fib3 = thread.calls[0]
        self.assertEqual(fib3.func, 'fib')

        # fib(3) == fib(2) + fib(1)
        self.assertEqual(2, len(fib3.callees))

        # fib(2) == fib(1) + fib(0)
        fib2 = fib3.callees[0]
        self.assertEqual(2, len(fib2.callees))

        # fib(1) == 0
        fib1 = fib2.callees[0]
        self.assertEqual(0, len(fib1.callees))


def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)


def bar():
    baz()


def baz():
    booyah()


def booyah():
    pass
