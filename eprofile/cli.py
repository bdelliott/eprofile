"""Set a trace function and track time in individual greenthreads"""

import eventlet
eventlet.monkey_patch()

import sys

from eprofile import trace


def main():
    from tests import single

    trace.enable()
    single.foo()
    trace.disable()
    sys.settrace(None)

    print "-"*80
    print "Trace info:"
    print "-"*80
    print

    threads = trace.threads
    for gid, thread in threads.iteritems():
        print "Thread %d:" % gid
        for call in thread.calls:
            call.pretty()


if __name__ == '__main__':
    main()
