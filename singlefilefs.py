#!/usr/bin/env python

import fuse
import time

import stat
import os
import errno
import sys
import io

class SingleFileFS(fuse.Fuse):
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

    def open (self, path, flags):
        if path != "/%s" % os.path.basename(self.source):
            return -errno.ENOENT
        return 0

    def read (self, path, length, offset):
        if path != "/%s" % os.path.basename(self.source):
            return -errno.ENOSYS

        self.file.seek(offset, io.SEEK_SET)
        return self.file.read(length)

# vim:set et sw=4 si:
