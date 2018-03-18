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
  print ("usage: %s file.tif [slice]" % sys.argv[0])
  sys.exit(2)
if sys.argv[1] in ['-h', '--help']:
  print ("usage: %s file.tif [slice]" % sys.argv[0])
  sys.exit(0)

slice = 0
if len(sys.argv) > 2:
  try:
    slice = int(sys.argv[2])
  except:
    pass

img = tifffile.imread(sys.argv[1])
if len(img.shape) == 3:
  if slice >= img.shape[0]:
    print ("Warn: specified slice geater than #of TIFF slice, showing 0")
    plt.imshow(img[0])
  else:
    plt.imshow(img[slice])
elif len(img.shape) == 2:
  plt.imshow(img)
else:
  print ("invalid dimension: %d" % len(img.shape))
  sys.exit(3)

plt.show()
sys.exit(0)

