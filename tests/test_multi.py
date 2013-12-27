import time

from eventlet import greenpool

from eprofile import fixtures
from eprofile import trace

import base



class MultiThreadTestCase(base.TestCase):

    def test_multi(self):
        # test multi threaded tracing

        gid = self.prof._gid()
        self.prof.runcall(fixtures.multi)

        threads = self.prof.threads
        print threads
        self.assertEqual(1, len(threads))
        raise
