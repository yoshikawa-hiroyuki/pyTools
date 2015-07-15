#! /usr/bin/env python
import sys, os
import struct
from SPH import *

if len(sys.argv) < 3:
    sys.exit('usage: %s infile.sph outfile.vol' % sys.argv[0])

ifile = sys.argv[1]
ofile = sys.argv[2]

sph = SPH()
if not sph.load(ifile):
    sys.exit('load failed: %s' % ifile)

ofp = open(ofile, 'wb')

# write header
sz = 12
ofp.write(struct.pack('5i', sz, sph._dims[0], sph._dims[1], sph._dims[2], sz))

sz = 8
ofp.write(struct.pack('ifii', sz, sph._step, sph._time, sz))

sz = 24
gro = [sph._org[0] + sph._pitch[0]*(sph._dims[0]-1),
       sph._org[1] + sph._pitch[1]*(sph._dims[1]-1),
       sph._org[2] + sph._pitch[2]*(sph._dims[2]-1)]
ofp.write(struct.pack('i6fi', sz, sph._org[0], sph._org[1], sph._org[2],
                      gro[0], gro[1], gro[2], sz))

# write data
SCALE = lambda x: int(float(x) / (sph._max[0] - sph._min[0]) * 255)

sz = sph._dims[0] * sph._dims[1] * sph._dims[2]
ofp.write(struct.pack('i', sz))
for i in range(sz):
    ofp.write(struct.pack('B', SCALE(sph._data[i])))
ofp.write(struct.pack('i', sz))

ofp.close()
sys.exit(0)
