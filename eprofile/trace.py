"""Set a trace function and track time in individual greenthreads"""
# set a trace function and do some basic profiling on where time is spent

import eventlet
eventlet.monkey_patch()

import sys
import time

from eventlet import greenthread
import prettytable


class Profiler(object):

    def __init__(self):
        self.threads = {}

        self.current = None  # current thread being traced

        # call once into the hub or we get errors about missing 'hub' in
        # threadlocal during tracing
        time.sleep(0)

    def runcall(self, func, *args, **kwargs):

        sys.settrace(self.trace)
        try:
            func(*args, **kwargs)
        finally:
            sys.settrace(None)
            self.tally()

    def _gid(self):
        return id(greenthread.getcurrent())

    def tally(self):
        # tally up timings
        for thread in self.threads.values():
            thread.tally()

    def trace(self, frame, event, arg):
        gid = self._gid()
        thread = self.threads.setdefault(gid, Thread(gid))

        # did the thread swap?
        if self.current and thread != self.current:
            now = time.time()

            # swapped, mark the old thread as suspended
            self.current.suspend(now)

            # if the new thread was suspended, mark it resumed
            thread.resume(now)

        self.current = thread

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


class Thread(object):
    def __init__(self, gid):
        self.gid = gid
        self.calls = []
        self.stack = []

        self.start = None  # wall clock start and end
        self.end = None

        self.suspend_start = None
        self.suspend_end = None

        self.time_total = 0  # total wall clock time for the thread
        self.time_running = 0  # time actually executing code
        self.time_suspended = 0  # cumulative suspension time

    def call(self, frame):
        code = frame.f_code
        filename = code.co_filename
        line = code.co_firstlineno
        func = code.co_name
        call = Call(filename, line, func)

        if len(self.stack) == 0:
            # the stack is empty, add to the top-level list of callees:
            self.calls.append(call)
        else:
            # mark another callee on the current stack frame
            self.stack[-1].add(call)

        # push it onto stack of the current execution path:
        self.stack.append(call)

    def line(self, frame):
        # new line or loop iteration - update timestamp on current call
        # in the stack
        call = self.stack[-1]
        call.update_touch()

    def resume(self, ts):
        # if thread was suspended, resume it
        if self.suspend_start:
            self.suspend_end = ts

            diff = self.suspend_end - self.suspend_start
            self.time_suspended += diff

            self.suspend_end = self.suspend_start = None

    def return_(self):
        call = self.stack.pop()
        call.finish()

    def suspend(self, ts):
        # mark it as no longer running
        self.suspend_start = ts

    def tally(self):
        # tally up final runtime timings
        self.start = self.calls[0].start

        # take either the end timestamp from the call returning or its most
        # recent touch value.  (We don't know for sure that all calls are
        # completed when tracing completes)
        if len(self.stack) == 0:
            lastcall = self.calls[-1]
            assert lastcall.end is not None
            self.end = lastcall.end
        else:
            lastcall = self.stack[-1]
            self.end = lastcall.touch

        self.time_total = self.end - self.start

        # actual time running is just wall time minus suspension time
        self.time_running = self.time_total - self.time_suspended

    def __repr__(self):
        # print the gid and top-level call
        return "%s :: %s" % (self.gid, self.calls[0].func)


class Call(object):
    def __init__(self, filename, line, func):
        self.filename = filename
        self.line = line
        self.func = func
        self.start = time.time()

        self.short_filename = filename.split('/')[-1]
        self.calls = []

        self.start = time.time()
        self.touch = self.start  # most recent timestamp for the call
        self.end = None

    def add(self, call):
        # add a callee
        self.calls.append(call)

    def desc(self):
        # short-description of the call
        return "%s:%d::%s" % (self.short_filename, self.line, self.func)

    def finish(self):
        self.end = time.time()

    def pretty(self, level=0):
        # pretty print the call execution path
        print "%s%s:%d :: %s" % (' ' * level, self.filename, self.line,
                                 self.func)

        # also render callees:
        level += 2
        for call in self.calls:
            call.pretty(level=level)

    def update_touch(self):
        self.touch = time.time()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "%s:%s" % (self.short_filename, self.func)
