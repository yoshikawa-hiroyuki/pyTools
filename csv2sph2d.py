#! /usr/bin/env python
# csv2sph2d
import sys, os
import numpy as np
try:
    from pySPH import SPH
except:
    sys.stderr.write('%s: can not import pySPH\n' % sys.argv[0])
    sys.exit(1)
    
srcf = ""
dstf = ""
if len(sys.argv) > 2:
    srcf = sys.argv[1]
    dstf = sys.argv[2]
else:
    sys.stderr.write("usage: %s srcfile.csv dstfile.sph\n" % sys.argv[0])
    sys.exit(1)

# open srcfile
try:
    sdat = np.loadtxt(srcf, comments='#', delimiter=',')
except:
    sys.stderr.write('%s: can not load from file: %s\n' % (sys.argv[0], srcf))
    sys.exit(1)

dims = [sdat.shape[1], sdat.shape[0], 1]
if dims[0] < 1 or dims[1] < 1:
    sys.stderr.write('%s: invalid dims: %s\n' % (sys.argv[0], str(dims)))
    sys.exit(1)

# create SPH
sph = SPH.SPH()
sph._veclen = 1
sph._dtype = sph.DT_SINGLE
sph._org = [0.0, 0.0, 0.0]
sph._pitch = [1.0, 1.0, 1.0]

# copy data
sph._dims[:] = dims[:]
dimSz = sph._dims[0] * sph._dims[1] * sph._dims[2]
sph._data = np.array(0, dtype=float)
sph._data.resize(dimSz)
sdat.resize(dimSz)
for idx in range(dimSz):
    sph._data[idx] = float(sdat[idx])

# write to dstf
try:
    sph.save(dstf)
except:
    sys.stderr.write('%s: save failed: %s\n' % (sys.argv[0], dstf))
    sys.exit(1)

sys.exit(0)
