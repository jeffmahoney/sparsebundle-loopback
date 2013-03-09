#!/usr/bin/env python

import sys
import os
import fuse

from sparsebundle import SparseBundle
import singlefilefs

source = None
if len(sys.argv) > 2:
        source = sys.argv[1]
        source = os.path.realpath(source)

        bundle = SparseBundle(source)
        print "Using %s" % os.path.basename(source)

if source is None:
    print >>sys.stderr, "Need source dir"
    sys.exit(1)

fuse.fuse_python_api = (0, 2)
fs = singlefilefs.SingleFileFS(source, bundle)
fs.flags = 0
fs.multithreaded = 0
fs.parse()
fs.main()

# vim:set et sw=4 si:
