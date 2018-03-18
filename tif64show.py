#! /usr/bin/env python
import sys
try:
  import tifffile
except:
  print ("can not import tifffile, not installed?")
  sys.exit(1)
try:
  import matplotlib.pyplot as plt
except:
  print ("can not import matplotlib.pyplot, not installed?")
  sys.exit(1)

if len(sys.argv) < 2:
  print ("usage: %s file.tif")
  sys.exit(2)

img = tifffile.imread(sys.argv[1])
if len(img.shape) == 3:
  plt.imshow(img[0])
elif len(img.shape) == 2:
  plt.imshow(img)
else:
  print ("invalid dimension: %d" % len(img.shape))
  sys.exit(3)

plt.show()
sys.exit(0)

