#! /usr/bin/env python
import sys
import struct
import numpy


srcf = ""
dstf = ""
if ( len(sys.argv) > 2 ):
    srcf = sys.argv[1]
    dstf = sys.argv[2]
else:
    sys.exit("usage: %s srcfile.fdv dstfile.d" % sys.argv[0])

# open srcfile
try:
    ifp = open(srcf, "rb")
except:
    sys.exit("open failed: %s" % srcf)


# header record
bo = '@'
buff = struct.unpack('i', ifp.read(4))
if buff[0] != 4:
    if sys.byteorder == 'little': bo = '>'
    else: bo = '<'
    
buff = struct.unpack(bo+'10i', ifp.read(40))
hasV = int(buff[0] / 100) != 0
hasS = int((buff[0] % 100) / 10) != 0
hasG = buff[0] % 10
if not hasS:
    sys.exit("no scalar data")
dims = (buff[6], buff[7], buff[8]);
dimSz = dims[0] * dims[1] * dims[2]
if dimSz < 1:
    sys.exit("invalid dims: %d x %d x %d" % (dims[0], dims[1], dims[2]))
dimSzXY = dims[0] * dims[1]

# time record
buff = struct.unpack(bo+'iifi', ifp.read(16))
step, ftime = (buff[1], buff[2])


# grid record
if hasG:
    print "skip grid data"
    ifp.read(4)
    for k in range(dims[2]):
        ifp.read(12*dimSzXY)
    ifp.read(4)


# open dstfile
try:
    ofp = open(dstf, 'wb')
except:
    sys.exit("open failed: %s" % dstf)
ofp.write(struct.pack(bo+'i', 12))
ofp.write(struct.pack(bo+'3i', dims[0], dims[1], dims[2]))
ofp.write(struct.pack(bo+'i', 12))

# scalar data record
ofp.write(ifp.read(4))
for k in range(dims[2]):
    ofp.write(ifp.read(dimSzXY*4))
ofp.write(ifp.read(4))

ifp.close()
ofp.close()

sys.exit(0)

