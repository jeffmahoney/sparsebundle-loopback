#!/usr/bin/env python

import fuse
import time
import stat
import os
import errno
import sys
import optparse

# Apple Time Machine uses a version of HFS+ that allows zero length
# regular files with a set number of hard links to exist without
# requiring the number of directory entries to exist to back the link
# count.
#
# The link count is overloaded to map the file to a lookup of
# /.HFS+ Private Directory Data\r/dirid_%d at the root of the file system.
#
# Further, the hierarchy of the file system is well-defined for the first
# few levels.
# /Backups.backupdb/<machines>/<timestamps>/<filesystem> contains
# the backup trees for each (machine,timestamp,fs) tuple. This
# FUSE implementation skips the first level of the tree and presents
# a file system with the list of machines backed-up in the root, with
# automatic lookups of the directory structure underneath the filesystem
# level.
#
# The implementation was inspired by the C++ tmfs implementation, found at
# https://github.com/abique/tmfs.git

class TMFS(fuse.Fuse):
    def __init__(self, hfsroot, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)

        hfsroot = os.path.realpath(hfsroot)

        self.backups = "%s/%s" % (hfsroot, "Backups.backupdb")
        self.private = "%s/%s" % (hfsroot, ".HFS+ Private Directory Data\r")

    def real_path(self, path):
        path = os.path.normpath(path)

        pcomps = path.split('/')

        # Nothing to resolve
        if len(pcomps) <= 3:
            path = os.path.realpath("%s/%s" % (self.backups, path))
            return path

        newpath = self.backups + "/" + '/'.join(pcomps[1:4])
        for comp in pcomps[4:]:
            newpath += "/%s" % comp

            try:
                st = os.lstat(newpath)
            except OSError, e:
                return newpath

            if not (st.st_mode & stat.S_IFREG or st.st_size > 0 ):
                return newpath

            private = "%s/dir_%d" % (self.private, st.st_nlink)

            if os.path.exists(private):
                newpath = private

        return newpath

    def readdir(self, path, offset):
        path = self.real_path(path)

        if not os.path.isdir(path):
            yield -errno.ENOTDIR

        entries = [ '.', '..' ]
        entries += os.listdir(path)
        for e in entries:
            yield fuse.Direntry(e)

    def getattr(self, path):
        path = self.real_path(path)
        try:
            return os.lstat(path)
        except OSError, e:
            return -e.errno

    def mythread ( self ):
        print '*** mythread'
        return -errno.ENOSYS

    def open (self, path, flags):
        path = self.real_path(path)
        if os.path.exists(path):
            return 0
        return -errno.ENOENT

    def read (self, path, length, offset):
        path = self.real_path(path)
        f = open(path)
        f.seek(offset, io.SEEK_SET)
        ret = f.read(length)
        f.close()
        return ret


    def readlink ( self, path ):
        path = self.real_path(path)
        return os.readlink(path)

if __name__ == '__main__':

    opts = fuse.FuseOptParse(usage=optparse.SUPPRESS_USAGE)
    (options, args) = opts.parse_args()

    if len(args) != 1:
        print >>sys.stderr, "usage: %s [opts] <source dir> <mountpoint>" % \
                            os.path.basename(sys.argv[0])
        opts.print_help()
        sys.exit(1)

    if opts.fuse_args.mountpoint in os.path.realpath(args[0]):
        print >>sys.stderr, "%s: source dir %s can't be under mountpoint %s" \
                            % (os.path.basename(sys.argv[0]),
                               os.path.realpath(args[0]),
                               opts.fuse_args.mountpoint)
        sys.exit(1)

    fuse.fuse_python_api = (0, 2)
    fs = TMFS(args[0])
    fs.flags = 0
    fs.multithreaded = 0
    fs.parse()
    fs.main()

# vim:set et sw=4 si:
