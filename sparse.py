#!/usr/bin/env python

import fuse
import time

import stat
import os
import errno
import sys
import io

class SparseFS(fuse.Fuse):
    def __init__(self, source, fileptr=None, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)

        self.source = source
        self.file = fileptr

        if not self.file:
            self.file = open(self.source, "rb")

        st = os.stat(source)

        self.uid = st.st_uid
        self.gid = st.st_gid

        # Get file size without stat
        self.file.seek(0, io.SEEK_END)
        self.size = self.file.tell()

        # Reset file position
        self.file.seek(0, io.SEEK_SET)

        print 'Init complete.'

    def readdir(self, path, offset):
        for e in '.', '..', os.path.basename(self.source):
            yield fuse.Direntry(e)

    def getattr(self, path):
        if path == "/":
            st = fuse.Stat()
            st.st_mode = stat.S_IFDIR | 0555
            st.st_nlink = 3
            st.st_atime = int(time.time())
            st.st_mtime = st.st_atime
            st.st_ctime = st.st_atime
            st.st_uid = self.uid
            st.st_gid = self.gid
            return st
        elif path == "/%s" % os.path.basename(self.source):
            st = fuse.Stat()
            st.st_mode = stat.S_IFREG | 0444
            st.st_nlink = 1
            st.st_atime = int(time.time())
            st.st_mtime = st.st_atime
            st.st_ctime = st.st_atime
            st.st_size = self.size
            st.st_uid = self.uid
            st.st_gid = self.gid
            return st

        return -errno.ENOENT

    def mythread ( self ):
        print '*** mythread'
        return -errno.ENOSYS

    def chmod ( self, path, mode ):
        print '*** chmod', path, oct(mode)
        return -errno.EACCES

    def chown ( self, path, uid, gid ):
        print '*** chown', path, uid, gid
        return -errno.EACCES

    def fsync ( self, path, isFsyncFile ):
        print '*** fsync', path, isFsyncFile
        return -errno.EACCES

    def link ( self, targetPath, linkPath ):
        print '*** link', targetPath, linkPath
        return -errno.EACCES

    def mkdir ( self, path, mode ):
        print '*** mkdir', path, oct(mode)
        return -errno.EACCES

    def mknod ( self, path, mode, dev ):
        print '*** mknod', path, oct(mode), dev
        return -errno.EACCES

    def open (self, path, flags):
        if path != "/%s" % os.path.basename(self.source):
            return -errno.ENOENT
        return 0

    def read (self, path, length, offset):
        if path != "/%s" % os.path.basename(self.source):
            return -errno.ENOSYS

        self.file.seek(offset, io.SEEK_SET)
        return self.file.read(length)

    def readlink ( self, path ):
        print '*** readlink', path
        return -errno.ENOSYS

    def release ( self, path, flags ):
        print '*** release', path, flags
        return -errno.EACCES

    def rename ( self, oldPath, newPath ):
        print '*** rename', oldPath, newPath
        return -errno.EACCES

    def rmdir ( self, path ):
        print '*** rmdir', path
        return -errno.EACCES

    def statfs ( self ):
        print '*** statfs'
        return -errno.ENOSYS

    def symlink ( self, targetPath, linkPath ):
        return -errno.EACCES

    def truncate ( self, path, size ):
        return -errno.EACCES

    def unlink ( self, path ):
        print '*** unlink', path
        return -errno.EACCES

    def utime ( self, path, times ):
        return -errno.EACCES

    def write ( self, path, buf, offset ):
        return -errno.EACCES

if __name__ == '__main__':
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
    fs = SparseFS(source, p)
    fs.flags = 0
    fs.multithreaded = 0
    fs.parse()
    fs.main()

# vim:set et sw=4 si:
