import time

from eprofile import callstate


class ThreadState(object):
    def __init__(self, gid):
        self.gid = gid
        self.calls = []
        self.stack = []

        self.start = None  # wall clock start and end
        self.end = None
        self.touch = None

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
        call = callstate.CallState(filename, line, func)

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

        if len(self.stack) == 0:
            self.end = self.calls[-1].end
        else:
            self.end = self.stack[-1].end

        self.time_total = self.end - self.start

        # actual time running is just wall time minus suspension time
        self.time_running = self.time_total - self.time_suspended

    def update_touch(self):
        self.touch = time.time()

    def __repr__(self):
        # print the gid and top-level call
        return "%s :: %s" % (self.gid, self.calls[0].func)
