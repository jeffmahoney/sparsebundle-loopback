#!/usr/bin/env python

import sys
import os
import fuse
import optparse

from sparsebundle import SparseBundle
import singlefilefs

opts = fuse.FuseOptParse(usage=optparse.SUPPRESS_USAGE)
(options, args) = opts.parse_args()

if len(args) != 1:
    print >>sys.stderr, "usage: %s [opts] <sparsebundle dir> <mountpoint>" % \
                        os.path.basename(sys.argv[0])
    opts.print_help()
    sys.exit(1)

source = os.path.realpath(args[0])
bundle = SparseBundle(source)
print "Using %s" % os.path.basename(source)

fuse.fuse_python_api = (0, 2)
fs = singlefilefs.SingleFileFS(source, bundle)
fs.flags = 0
fs.multithreaded = 0
fs.parse()
fs.main()

# vim:set et sw=4 si:
