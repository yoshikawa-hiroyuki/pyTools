#! /usr/bin/env python
import sys
import struct
import numpy

import SPH;


srcf = ""
dstf = ""
if ( len(sys.argv) > 2 ):
    srcf = sys.argv[1]
    dstf = sys.argv[2]
else:
    sys.exit("usage: %s srcfile.fdv dstfile.sph" % sys.argv[0])

# open srcfile
try:
    ifp = open(srcf, "rb")
except:
    sys.exit("open failed: %s" % srcf)


# header record
bo = '@'
buff = struct.unpack('i', ifp.read(4))
if buff[0] != 12:
    if sys.byteorder == 'little': bo = '>'
    else: bo = '<'
    
buff = struct.unpack(bo+'4i', ifp.read(16))
dims = (buff[0], buff[1], buff[2]);
dimSz = dims[0] * dims[1] * dims[2]
if dimSz < 1:
    sys.exit("invalid dims: %d x %d x %d" % (dims[0], dims[1], dims[2]))


# time record
buff = struct.unpack(bo+'iifi', ifp.read(16))
step, ftime = (buff[1], buff[2])


# bbox record
buff = struct.unpack(bo+'i6fi', ifp.read(32))
org = (buff[1], buff[2], buff[3])
gro = (buff[4], buff[5], buff[6])


# data record
ifp.read(4) # skip
bdata = struct.unpack(str(dimSz)+'B', ifp.read(dimSz))

ifp.close()


# convert
sph = SPH.SPH()
sph._dims[:] = dims[:]
sph._org[:] = org[:]
sph._pitch[0] = (gro[0] - org[0]) / dims[0]
sph._pitch[1] = (gro[1] - org[1]) / dims[1]
sph._pitch[2] = (gro[2] - org[2]) / dims[2]
sph._time = ftime
sph._step = step

sph._data = numpy.array(0, dtype=float)
sph._data.resize(dimSz)

for i in range(dimSz):
    sph._data[i] = float(bdata[i])

sph.save(dstf)

