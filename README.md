sparsebundle-loopback
=====================

A FUSE wrapper to present MacOS-style sparsebundle bands as a single file under Linux

Use case:

When using a netatalk server under Linux as a Time Machine device, MacOS
will store the device as a sparsebundle. The sparsebundle is implemented as
several plists and a directory full of band files.

This FUSE wrapper parses the plists and reconstructs a unified file from
the bands and presents it as a single file under the specified mount point.

I currently use it in the following manner to access Time Machine backups
from Linux directly. AFP while using the sparsebundle bands is extremely
slow over links with limited bandwidth, making using Time Machine directly
difficult when traveling.

sparse.py itself depends on libplist: http://cgit.sukimashita.com/libplist.git
The usage below depends on tmfs: https://github.com/abique/tmfs.git

./sparse.py /path/to/<name>.sparsebundle /mnt
losetup /dev/loop# /mnt/<name>.sparsebundle
mount -r -t hfsplus /dev/loop# /mnt2
./tmfs /mnt2 /mnt3

/mnt3 will now contain the Time Machine backup file system, with directories
named with the dates the backup was taken, each containing the backup from
that date.

I anticipate future versions will wrap all of the above steps into one
for easier use.
