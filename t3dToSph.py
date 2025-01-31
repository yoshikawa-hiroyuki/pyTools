#! /usr/bin/env python
import sys, os
try:
    import numpy as np
except:
    sys.exit('%s: can not import numpy' % sys.argv[0])

try:
    from PIL import Image
    from PIL import ImageSequence
except:
    sys.exit('%s: can not import PIL' % sys.argv[0])

try:
    from pySPH import SPH
except:
    sys.exit('%s: can not import pySPH' % sys.argv[0])


if len(sys.argv) < 3:
    sys.exit('usage: %s infile.tif outfile.sph' % sys.argv[0])

try:
    img = Image.open(sys.argv[1])
except:
    sys.exit('%s: load failed: %s' % (sys.argv[0], sys.argv[1]))

try:
   numpage = img.n_frames
except:
   numpage = img.n_frames # bug compatible ...
if numpage < 2:
    sys.exit('%s: not 3D TIFF: %s' % (sys.argv[0], sys.argv[1]))

sph = SPH.SPH()
sph._veclen = 1
sph._dtype = sph.DT_SINGLE
sph._org = [0.0, 0.0, 0.0]
sph._pitch = [1.0, 1.0, 1.0]

sph._dims[0] = img.size[0]
sph._dims[1] = img.size[1]
sph._dims[2] = numpage
dimSz = sph._dims[0] * sph._dims[1] * sph._dims[2]
#sph._data = numpy.array(0, dtype=float)
#sph._data.resize(dimSz)

data = np.ndarray((numpage, img.size[1], img.size[0]))

for i, page in enumerate(ImageSequence.Iterator(img)):
    page_conv = np.asarray(page.convert('F')).reshape((img.size[1], img.size[0]))
    data[i,:,:] = page_conv[:,:]
    continue

sph._data = data.reshape(dimSz)

try:
    sph.save(sys.argv[2])
except:
    sys.exit('%s: save failed: %s' % (sys.argv[0], sys.argv[2]))

sys.exit(0)
