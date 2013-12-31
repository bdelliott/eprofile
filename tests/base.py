import eventlet
eventlet.monkey_patch()

import mox
import unittest

import eprofile


class TestCase(unittest.TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        self.mox = mox.Mox()
        self.stubs = self.mox.stubs

        self.prof = eprofile.Profiler()

    def tearDown(self):
        super(TestCase, self).tearDown()
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
