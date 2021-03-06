"""Set a trace function and track time in individual greenthreads"""

import eventlet
eventlet.monkey_patch()

import optparse
import sys

import eprofile
from eprofile import fixtures


def main():
    parser = optparse.OptionParser()
    opts, args = parser.parse_args()

    if len(args) == 0:
        func = fixtures.foo
        args = [1]
    else:
        funcname = args.pop(0)
        func = getattr(fixtures, funcname)

    _exec(func, *args)


def _exec(func, *args):
    prof = eprofile.Profiler()
    prof.runcall(func, *args)

    print "-"*80
    print "Trace info:"
    print "-"*80
    print

    threads = prof.threads
    for gid, thread in threads.iteritems():
        print "Thread %d:" % gid
        for call in thread.calls:
            call.pretty()

    print "-" * 80
    prof.print_stats()

    print "-" * 80
    print "Cumulative:"
    print "-" * 80
    prof.print_cumulative()

    print "-" * 80
    print "Localtime:"
    print "-" * 80
    prof.print_localtime()
