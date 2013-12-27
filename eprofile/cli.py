"""Set a trace function and track time in individual greenthreads"""

import eventlet
eventlet.monkey_patch()

import sys

from eprofile import fixtures
from eprofile import trace


def main():

    prof = trace.Profiler()
    prof.runcall(fixtures.foo)

    print "-"*80
    print "Trace info:"
    print "-"*80
    print

    threads = prof.threads
    for gid, thread in threads.iteritems():
        print "Thread %d:" % gid
        for call in thread.calls:
            call.pretty()


if __name__ == '__main__':
    main()
