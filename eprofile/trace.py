"""Set a trace function and track time in individual greenthreads"""
# set a trace function and do some basic profiling on where time is spent

#import eventlet
#eventlet.monkey_patch()

from eventlet import greenthread
import sys
import time

import tests


class Profiler(object):

    def __init__(self):
        self.threads = {}

        # call once into the hub or we get errors about missing 'hub' in
        # threadlocal during tracing
        time.sleep(0)

    def runcall(self, func, *args, **kwargs):

        sys.settrace(self.trace)
        try:
            func(*args, **kwargs)
        finally:
            sys.settrace(None)

    def _gid(self):
        return id(greenthread.getcurrent())

    def trace(self, frame, event, arg):
        gid = self._gid()
        x = len(self.threads)
        thread = self.threads.setdefault(gid, Thread(gid))
        y = len(self.threads)
        if y > x:
            print "Added thread: %s" % gid

        if event == 'call':
            # interpreter is calling a new function
            thread.call(frame)

            return self.trace

        elif event == 'line':
            # interpreter is executing a new line or iteration of a loop.
            # ignore.
            pass

        elif event == 'return':
            # pop a call off the thread's state stack
            thread.return_()

        elif event == 'exception':
            exc, value, tb = arg
            print "**** exception ****"
            print exc
            print value
            print tb
            import traceback
            traceback.print_tb(tb)

            raise exc, value, tb

        else:
            raise SystemExit(event)


class Thread(object):
    def __init__(self, gid):
        self.gid = gid
        self.calls = []
        self.stack = []

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

    def return_(self):
        call = self.stack.pop()
        call.end()

    def __str__(self):
        # pretty print the execution path
        for call in self.calls:
            print call


class Call(object):
    def __init__(self, filename, line, func):
        self.filename = filename
        self.line = line
        self.func = func
        self.start = time.time()

        self.callees = []

    def add(self, call):
        # add a callee
        self.callees.append(call)

    def end(self):
        self.end = time.time()

    def pretty(self, level=0):
        # pretty print the call execution path
        print "%s%s:%d :: %s" % (' ' * level, self.filename, self.line,
                                 self.func)

        # also render callees:
        level += 2
        for callee in self.callees:
            callee.pretty(level=level)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.func
