import base

from eprofile import fixtures


class StatsThreadTestCase(base.TestCase):

    def test_cumulative(self):
        # test ability to display by cumulative time

        gid = self.prof._gid()
        self.prof.runcall(fixtures.outer)

        threads = self.prof.threads
        self.assertEqual(1, len(threads))

        thread = threads.values()[0]
        outer = thread.calls[0]
        self.assertEqual('outer', outer.func)

        inner = outer.calls[0]
        self.assertEqual('inner', inner.func)

        # fake the timing information
        self.prof.start = 1
        self.prof.end = 5
        outer.start = 1
        outer._end = 5
        inner.start = 3
        inner._end = 5

        self.prof.tally()
        l = self.prof.aggregate_timings()
        l.sort(key=lambda x: x['cum'], reverse=True)

        # should sort longer cumulative time 1st
        timing = l[0]
        self.assertEqual('outer', timing['code'].func)
        self.assertEqual(4, timing['cum'])

        timing = l[1]
        self.assertEqual('inner', timing['code'].func)
        self.assertEqual(2, timing['cum'])
