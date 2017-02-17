#! /usr/bin/env python
import sys, os
import numpy
try:
    import libtiff3d
except:
    sys.exit('%s: can not import libtiff3d, see https://github.com/joe-jordan/pylibtiff3d' % sys.argv[0])
try:
    from SPH import *
except:
    sys.exit('%s: can not import SPH' % sys.argv[0])

if len(sys.argv) < 3:
    sys.exit('usage: %s infile.tif outfile.sph' % sys.argv[0])

try:
    t = libtiff3d.TIFF3D.open(sys.argv[1])
    td = t.read_image()
    t.close()
except:
    sys.exit('%s: load failed: %s' % (sys.argv[0], sys.argv[1]))

if len(td.shape) != 3:
    sys.exit('%s: not 3D TIFF: %s' % (sys.argv[0], sys.argv[1]))

sph = SPH.SPH()
sph._veclen = 1
sph._dtype = sph.DT_SINGLE
sph._org = [0.0, 0.0, 0.0]
sph._pitch = [1.0, 1.0, 1.0]

sph._dims[0] = td.shape[2]
sph._dims[1] = td.shape[1]
sph._dims[2] = td.shape[0]
dimSz = sph._dims[0] * sph._dims[1] * sph._dims[2]
sph._data = numpy.array(0, dtype=float)
sph._data.resize(dimSz)

idx = 0
try:
    for k in range(sph._dims[2]):
        for j in range(sph._dims[1]):
            for i in range(sph._dims[0]):
                sph._data[idx] = float(td[k][j][i])
                idx += 1
except:
    print 'index out of bounds (%d: %d, %d, %d)' \
        % (idx, i, j, k)
    sys.exit(1)

try:
    sph.save(sys.argv[2])
except:
    sys.exit('%s: save failed: %s' % (sys.argv[0], sys.argv[2]))

sys.exit(0)
