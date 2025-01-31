#! /usr/bin/env python
#
# spx2sph
#
import sys
import struct
import string
import zlib
import numpy

srcf = ""
dstf = ""
if ( len(sys.argv) > 2 ):
    srcf = sys.argv[1]
    dstf = sys.argv[2]
else:
    sys.exit("usage: %s srcfile.spx dstfile.sph" % sys.argv[0])

# open srcfile
ifp = open(srcf, "rb")

# attribute record
buff = struct.unpack('cccciiiiiiiq', ifp.read(40))
if ( buff[0] != 'S' or buff[1] != 'P' or buff[2] != 'X' ):
    print("invalid file: not SPX")
    sys.exit(-1)

dimension = buff[4]
vlen = buff[5]
dtype = buff[6]
gc = buff[7]
rlen = buff[8]
crddef = buff[9]
aux = buff[10]
blksize = buff[11]

print("dimension = ", dimension)
if ( dimension < 1 or dimension > 3 ):
    ifp.close()
    print("invalid dimension: %s" % dimension)
    sys.exit(-1)

print("vlen = ", vlen)
if ( vlen < 1 ):
    ifp.close()
    print("invalid vlen: < 1")
    sys.exit(-1)

print("dtype = ", dtype)
if ( dtype != 1 and dtype != 2 and dtype != 3 ):
    ifp.close()
    print("invalid dtype: ", dtype)
    sys.exit(-1)
if dtype == 3: dtype = 2

print("gc = ", gc)

print("rlen = ", rlen,)
if ( rlen == 4 ):
    print("(single precision)")
    rdType = 1
elif ( rlen == 8 ):
    print("(double precision)")
    rdType = 2
else:
    ifp.close()
    print("invalid rlen: ", rlen)
    sys.exit(-1)

print("crddef = ", crddef,)
if ( crddef == 1 ):
    print("(regular)")
elif ( crddef == 2 ):
    print("(collocate)")
elif ( crddef == 3 ):
    print("(staggered 1)")
elif ( crddef == 4 ):
    print("(staggered 2)")
else:
    ifp.close()
    print("invalid crddef: unknown type")
    sys.exit(-1)

print("aux = ", aux,)

print("blksize = ", blksize,)
if ( blksize == 0 ):
    print("(uncompressed)")
elif ( blksize > 0 ):
    print("(compressed)")
else:
    ifp.close()
    print("invalid blksize")
    sys.exit(-1)

# size record
buff = struct.unpack('qqq', ifp.read(24))
dims = (buff[0], buff[1], buff[2])
print("dims = ", dims)

# org record
if ( rlen == 4 ):
    buff = struct.unpack('fff', ifp.read(12))
else:
    buff = struct.unpack('ddd', ifp.read(24))
org = (buff[0], buff[1], buff[2])
print("org = ", org)
    
# pitch record
if ( rlen == 4 ):
    buff = struct.unpack('fff', ifp.read(12))
else:
    buff = struct.unpack('ddd', ifp.read(24))
pitch = (buff[0], buff[1], buff[2])
print("pitch = ", pitch)

# time record
if ( rlen == 4 ):
    buff = struct.unpack('qf', ifp.read(12))
else:
    buff = struct.unpack('qd', ifp.read(16))
step, ftime = (buff[0], buff[1])
print("step = %d, time = %f" % (step, ftime))


# open dstfile
ofp = open(dstf, "wb")

# write header
ofp.write(struct.pack('4i', 8, dtype, rdType, 8))

# write size
if rdType == 1:
    ofp.write(struct.pack('5i', 12, dims[0], dims[1], dims[2], 12))
else:
    ofp.write(struct.pack('i', 24))
    ofp.write(struct.pack('3q', dims[0], dims[1], dims[2]))
    ofp.write(struct.pack('i', 24))
    
# write org
if rdType == 1:
    ofp.write(struct.pack('i3fi', 12, org[0], org[1], org[2], 12))
else:
    ofp.write(struct.pack('i', 24))
    ofp.write(struct.pack('3d', org[0], org[1], org[2]))
    ofp.write(struct.pack('i', 24))

# write pitch
if rdType == 1:
    ofp.write(struct.pack('i3fi', 12, pitch[0], pitch[1], pitch[2], 12))
else:
    ofp.write(struct.pack('i', 24))
    ofp.write(struct.pack('3d', pitch[0], pitch[1], pitch[2]))
    ofp.write(struct.pack('i', 24))

# write time
if rdType == 1:
    ofp.write(struct.pack('iifi', 8, step, ftime, 8))
else:
    ofp.write(struct.pack('i', 16))
    ofp.write(struct.pack('qd', step, ftime))
    ofp.write(struct.pack('i', 16))


# process data block
buffSz = dims[0] * dims[1] * dims[2]
if dtype != 1: buffSz = buffSz * 3
if rdType != 2: buffSz = buffSz * 2
ofp.write(struct.pack('i', buffSz))

if ( rlen == 4 ):
    packStr = 'f'
elif ( rlen == 8 ):
    packStr = 'd'

buff = struct.unpack('q', ifp.read(8))
zblkSz = buff[0]
while ( zblkSz ):
    str = ifp.read(zblkSz)
    if ( blksize != 0 ):
        dstr = zlib.decompress(str)
        ofp.write(dstr)
    else:
        ofp.write(str)

    buff = struct.unpack('q', ifp.read(8))
    zblkSz = buff[0]

ofp.write(struct.pack('i', buffSz))

ifp.close()
ofp.close()
