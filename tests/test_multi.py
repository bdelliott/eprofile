from eprofile import fixtures

import base


class MultiThreadTestCase(base.TestCase):

    def _workers(self):
        # helper functions to identify the greenthreads that ran the fixture
        # code
        workers = []

        threads = self.prof.threads.values()

        for thread in threads:
            call = thread.calls[0]
            if call.short_filename == 'greenthread.py' and \
               call.func == 'main':
                workers.append(thread)

        return workers

    def test_multi(self):
        # test multi threaded tracing

        gid = self.prof._gid()
        self.prof.runcall(fixtures.multi)

        threads = self.prof.threads
        self.assertTrue(threads >= 2)

        for gid, thread in threads.iteritems():
            # some threads may still have items on the stack
            self.assertTrue(len(thread.stack) >= 0)

        workers = self._workers()

        for worker in workers:
            # make sure each worker thread in the pool called
            # 'foo' and 'bar'
            maincall = worker.calls[0]
            self.assertEqual('main', maincall.func)

            foocall = maincall.calls[0]
            self.assertEqual('foo', foocall.func)

            barcall = foocall.calls[0]
            self.assertEqual('bar', barcall.func)

            sleepcall = barcall.calls[0]
            self.assertEqual('sleep', sleepcall.func)

    def test_thread_swap(self):
        # test tracking of current thread and swaps
        self.prof.runcall(fixtures.swap)

        # one of the threads should have at least 0.2 secs of suspended time.
        workers = self._workers()

        # whichever worker called 'wait' should have >= 0.2s suspended time
        workers = [w for w in workers if w.calls[0].calls[0].func == 'wait']
        self.assertEqual(1, len(workers))

        worker = workers[0]
        self.assertTrue(worker.time_suspended >= 0.2)

    def test_thread_runtime(self):
        # thread cumulative runtime should be a basically the sum of its
        # calls' runtimes
        self.stubs.Set(self.prof, '_gid', lambda: 1)

        # add 2 top-level calls to the profiler
        self.prof.trace(Frame(), 'call', None)
        self.prof.trace(Frame(), 'return', None)

        self.prof.trace(Frame(), 'call', None)
        self.prof.trace(Frame(), 'return', None)

        self.assertEqual(1, len(self.prof.threads))

        self.prof.start = 1
        self.prof.end = 5

        # add times to the calls
        thread = self.prof.threads.values()[0]
        self.assertEqual(2, len(thread.calls))

        thread.calls[0].start = 1
        thread.calls[0]._end = 2

        thread.calls[1].start = 3
        thread.calls[1]._end = 5

        # toss in one sec of suspend time
        thread.time_suspended = 1

        self.prof.tally()
        self.assertEqual(1, thread.start)
        self.assertEqual(5, thread.end)
        self.assertEqual(4, thread.time_total)
        self.assertEqual(3, thread.time_running)


class Code(object):
    co_filename = 'foo.py'
    co_firstlineno = 123
    co_name = 'foo'


class Frame(object):
    f_code = Code()
