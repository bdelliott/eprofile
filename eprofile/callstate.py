import time


class CallState(object):
    def __init__(self, filename, line, func):

        self.code = CodePoint(filename, line, func)
        self.start = time.time()

        self.calls = []

        self.start = time.time()
        self.touch = self.start  # most recent timestamp for the call
        self._end = None

        self.suspend_time = 0
        self.suspend_start = None

    def add(self, call):
        # add a callee
        self.calls.append(call)

    def desc(self):
        # short-description of the call
        return "%s:%d::%s" % (self.short_filename, self.line, self.func)

    @property
    def end(self):
        # take either the end timestamp from the call returning or its most
        # recent touch value.  (We don't know for sure that all calls are
        # completed when tracing completes)
        if self._end is None:
            return self.touch
        else:
            return self._end

    @property
    def filename(self):
        return self.code.filename

    def finish(self):
        self._end = time.time()

    @property
    def func(self):
        return self.code.func

    @property
    def line(self):
        return self.code.line

    def pretty(self, level=0):
        # pretty print the call execution path
        print "%s%s:%d :: %s" % (' ' * level, self.filename, self.line,
                                 self.func)

        # also render callees:
        level += 2
        for call in self.calls:
            call.pretty(level=level)

    @property
    def short_filename(self):
        return self.code.short_filename

    def resume(self):
        self.suspend_time += self.suspend_start
        self.suspend_start = None

    def suspend(self):
        self.suspend_start = time.time()

    def update_touch(self):
        self.touch = time.time()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "%s:%s" % (self.short_filename, self.func)


class CodePoint(object):

    def __init__(self, filename, line, func):
        self.filename = filename
        self.short_filename = filename.split('/')[-1]
        self.line = line
        self.func = func

    def __hash__(self):
        return hash((self.filename, self.line, self.func))

    def __eq__(self, other):
        return (self.filename == other.filename and
                self.line == other.line and
                self.func == other.func)

    def __str__(self):
        return "%s:%d::%s" % (self.filename, self.line, self.func)
