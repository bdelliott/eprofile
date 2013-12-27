import eventlet
eventlet.monkey_patch()

import unittest

from eprofile import trace


class TestCase(unittest.TestCase):
    def setUp(self):
        self.prof = trace.Profiler()
