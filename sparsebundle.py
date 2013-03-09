#!/usr/bin/env python

debug = False

import plistlib
import os
import io
if debug:
    import sys

def prdebug(text):
    if debug:
        print >>sys.stderr, text

class SparseBundle(io.RawIOBase):
    def __init__(self, dirname):
        if dirname is None:
            raise IOError("dirname can't be None")
        dirname = os.path.realpath(dirname)
        if not os.path.exists(dirname):
            raise IOError("%s does not exist." % dirname)
        if not os.path.isdir(dirname):
            raise IOError("%s is not a directory." % dirname)
        if not os.path.exists("%s/Info.plist" % dirname):
            raise IOError("%s/Info.plist does not exist." % dirname)

        p = plistlib.readPlist("%s/Info.plist" % dirname)
        if p['diskimage-bundle-type'] != 'com.apple.diskimage.sparsebundle':
            raise IOError("Unsupported bundle type %s" % p['diskimage-bundle-type'])

        self.source = dirname
        self.offset = 0
        self.band_size = int(p['band-size'])
        self.size = int(p['size'])
        self.band_files = {}
        self.band_lru = []
        self.max_file_cache = 64

    def open_band(self, offset):
        band = offset / self.band_size
        if not band in self.band_files:
            prdebug("Opening band %x" % band)
            f = open("%s/bands/%x" % (self.source, band), "rb")
            self.band_files[band] = f
            self.band_lru.append(band)
            if len(self.band_lru) > self.max_file_cache:
                oldband = self.band_lru[0]
                del self.band_files[oldband]
                self.band_lru.remove(oldband)
        else:
            prdebug("Pinging band %x" % band)
            self.band_lru.remove(band)
            self.band_lru.append(band)

        self.band_files[band].seek(offset % self.band_size, io.SEEK_SET)
        return band

    def readinto(self, buf):
        if self.offset < 0 or self.offset >= self.size:
            return 0

        length = len(buf)
        if debug:
            for i in range(0,length):
                buf[i] = 0

        buf_offset = 0
        while length > 0:
            band_offset = self.offset % self.band_size
            chunk = min(self.band_size - band_offset, length)

            try:
                band = self.open_band(self.offset)
                sparse_read = False
            except IOError, e:
                sparse_read = True
                band = None
            except Exception, e:
                raise IOError("Can't open band file %x: %s" % \
                              ((self.offset / self.band_size), str(e)))

            start = buf_offset
            end = start + chunk
            if band is not None:
                v = memoryview(buf)
                r = self.band_files[band].readinto(v[start:end])
                del v
            else:
                prdebug("Zeroing %d:%d" % (start, end))
                for i in range(start,end):
                    buf[i] = 0
            buf_offset += chunk
            length -= chunk
            self.offset += chunk

        return buf_offset
    
    def seekable():
        return True

    def readable():
        return True

    def writable():
        return False

    def close(self):
        for b in self.band_files:
            self.band_files[b].close()
        del self.band_files
        self.band_files = {}


    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            self.offset = offset
        elif whence == io.SEEK_CUR:
            self.offset += offset
        elif whence == io.SEEK_END:
            self.offset = self.size + whence
        else:
            raise IOError("Illegal whence %d" % whence)

        return self.offset

    def tell(self):
        return self.offset


    def write(self, buf):
        raise IOError("SparseBundle implementation is read-only.")

if __name__ == '__main__':
    path = "/home/jeffm/test image.sparsebundle"
    f = SparseBundle(path)
    f.seek(f.band_size * 2 - 512)
    r = f.read(1024)

    print r
    f.close()
    del f

# vim:set et sw=4 si:
