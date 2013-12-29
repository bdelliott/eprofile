import eventlet
eventlet.monkey_patch()

import mox
import unittest

from eprofile import trace


class TestCase(unittest.TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        self.mox = mox.Mox()
        self.stubs = self.mox.stubs

        self.prof = trace.Profiler()

    def tearDown(self):
        super(TestCase, self).tearDown()
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
