"""Set a trace function and track time in individual greenthreads"""
# set a trace function and do some basic profiling on where time is spent

import pickle
import sys
import time

from eventlet import greenthread
import prettytable

from eprofile import threadstate


class Profiler(object):

    def __init__(self):
        self.start = None
        self.end = None
        self.time_total = None  # total time under profiling

        self.threads = {}

        self.current = None  # current thread being traced

        # call once into the hub or we get errors about missing 'hub' in
        # threadlocal during tracing
        time.sleep(0)

    def runcall(self, func, *args, **kwargs):

        self.start = time.time()
        print "Starting trace of %s" % func.__name__

        sys.settrace(self.trace)
        try:
            rv = func(*args, **kwargs)
        finally:
            sys.settrace(None)

        self.end = time.time()

        t = self.end - self.start
        print " .. Completed trace of %s in %0.2f secs." % (func.__name__, t)

        print "Tallying stats"
        t1 = time.time()
        self.tally()
        t2 = time.time()
        t = t2 - t1
        print " .. Completed tally in %0.2f secs." % t

        return rv

    def _gid(self):
        return id(greenthread.getcurrent())

    @staticmethod
    def load(filename):
        f = open(filename, "rb")
        profiler = pickle.load(f)
        f.close()
        return profiler

    def save(self, filename):
        # save to a file
        f = open(filename, "wb")
        pickle.dump(self, f)
        f.close()

    def tally(self):
        # tally up timings
        self.time_total = self.end - self.start

        for thread in self.threads.values():
            thread.tally()

    def trace(self, frame, event, arg):
        gid = self._gid()
        thread = self.threads.setdefault(gid, threadstate.ThreadState(gid))

        # did the thread swap?
        if self.current and thread != self.current:
            now = time.time()

            # swapped, mark the old thread as suspended
            self.current.suspend(now)

            # if the new thread was suspended, mark it resumed
            thread.resume(now)

        self.current = thread

        thread.update_touch()

        # process the event
        if event == 'call':
            # interpreter is calling a new function
            thread.call(frame)

            return self.trace

        elif event == 'line':
            # interpreter is executing a new line or iteration of a loop.
            thread.line(frame)

        elif event == 'return':
            # pop a call off the thread's state stack

            # note: this gets called with arg == None for exceptions being
            # raised
            thread.return_()

        elif event == 'exception':
            # don't do anything special with these, just note the timers
            # and thread swaps
            #
            #exc, val, tb = arg
            #print "**** exception ****"
            #print exc
            #print val
            #print tb
            #code = frame.f_code
            #print code.co_filename
            #print code.co_firstlineno
            #print code.co_name
            pass

        else:
            raise SystemExit(event)

    def print_stats(self):
        cols = ['GID', 'Entry', 'Run time', 'Suspend time']
        t = prettytable.PrettyTable(cols)

        for thread in self.threads.values():
            tr = "%0.4f" % thread.time_running
            ts = "%0.4f" % thread.time_suspended
            row = [thread.gid, thread.calls[0].desc(), tr, ts]
            t.add_row(row)

        print t

    def aggregate_timings(self):
        # walk the call trees and calculate aggregate timings across all
        # greenthreads
        d = {}

        def _walk(call, d):
            assert call.start
            assert call.touch
            secs = call.end - call.start

            key = call.code

            default = {'cum': 0, 'local': 0, 'suspend': 0,
                       'num': 0, 'code': call.code}
            timing = d.setdefault(key, default)

            timing['num'] += 1
            timing['cum'] += secs  # add cumulative time

            # recurse through the subtree of calls made
            subcum = 0

            for call in call.calls:
                subcum += _walk(call, d)

            # subtract the cumulative time spent in calls and we get the
            # localtime spent in the current function
            local = secs - subcum
            timing['local'] += local

            # break out the suspended time
            suspend = local - call.suspend_time
            timing['suspend'] = suspend

            # retun cumulative time spent in this subset of the call tree
            return secs

        for thread in self.threads.values():
            for call in thread.calls:
                _walk(call, d)

        return d.values()

    def print_cumulative(self):
        l = self.aggregate_timings()

        # sort by most cumulative time
        l.sort(key=lambda x: x['cum'], reverse=True)

        print "Cumulative call data:"
        t = prettytable.PrettyTable(['Code point', 'Secs', 'Numcalls'])

        for timing in l:
            secs = "%0.4f" % timing['cum']
            t.add_row((timing['code'], secs, timing['num']))

        print t

    def print_localtime(self):
        l = self.aggregate_timings()

        # sort by most cumulative time
        l.sort(key=lambda x: x['local'], reverse=True)

        print "Localtime call data:"
        t = prettytable.PrettyTable(['Code point', 'Secs', 'Suspend', 'Numcalls'])

        for timing in l:
            secs = "%0.4f" % timing['local']
            suspend = "%0.4f" % timing['suspend']
            t.add_row((timing['code'], secs, suspend, timing['num']))

        print t
