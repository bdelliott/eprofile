import base

from eprofile import fixtures
from eprofile import trace


class SingleThreadTestCase(base.TestCase):

    def test_single(self):
        # test single threaded tracing

        gid = self.prof._gid()
        self.prof.runcall(fixtures.fib, 3)

        threads = self.prof.threads
        self.assertEqual(1, len(threads))
        self.assertEqual(gid, threads.keys()[0])

        thread = threads.values()[0]
        # stack should be empty
        self.assertEqual(0, len(thread.stack))

        # should be 1 top-level call
        self.assertEqual(1, len(thread.calls))

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
