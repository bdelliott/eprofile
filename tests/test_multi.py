from eprofile import fixtures

import base


class MultiThreadTestCase(base.TestCase):

    def test_multi(self):
        # test multi threaded tracing

        gid = self.prof._gid()
        self.prof.runcall(fixtures.multi)

        threads = self.prof.threads
        self.assertTrue(threads >= 2)
        
        workers = []

        for gid, thread in threads.iteritems():
            # some threads may still have items on the stack
            self.assertTrue(len(thread.stack) >= 0)

            # the actual greenthreads that did the work in the pool
            # are spawned in greenthread.py's main() func
            call = thread.calls[0]
            if (call.short_filename == 'greenthread.py' and
                call.func == 'main'):
                workers.append(thread)

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
