#! /usr/bin/env python
#
# sphEndianConv
#
import sys
import struct
import string
import zlib

srcf = ""
dstf = ""
if len(sys.argv) > 2:
    srcf = sys.argv[1]
    dstf = sys.argv[2]
else:
    sys.exit("usage: %s srcfile.sph dstfile.sph" % sys.argv[0])

# open srcfile
ifp = open(srcf, "rb")

# attribure record
ibo = '<'
obo = '>'
header = ifp.read(16)
buff = struct.unpack(ibo+'4i', header)
svType = buff[1]
dType = buff[2]
if svType != 1 and svType != 2:
    ibo = '>'
    obo = '<'
    buff = struct.unpack(ibo+'iiii', header)
    svType = buff[1]
    dType = buff[2]
    if svType != 1 and svType != 2:
        print("invalid svType: not 1 nor 2")
        sys.exit(-1)
if dType != 1 and dType != 2:
    print("invalid dType: not 1 nor 2")
    sys.exit(-1)

if svType == 1:
    vlen = 1
else:
    vlen = 3
if dType == 1:
    rlen = 4
else:
    rlen = 8

# size record
if dType == 1:
    buff = struct.unpack(ibo+'5i', ifp.read(20))
else:
    buff = struct.unpack(ibo+'i3qi', ifp.read(32))
dims = (buff[1], buff[2], buff[3])
dimSz = dims[0] * dims[1] * dims[2]
if dimSz < 1:
    print("invalid dims: %d x %d x %d" % (dims[0], dims[1], dims[2]))
    sys.exit(-1)

# org record
if dType == 1:
    buff = struct.unpack(ibo+'i3fi', ifp.read(20))
else:
    buff = struct.unpack(ibo+'i3di', ifp.read(32))
org = (buff[1], buff[2], buff[3])

# pitch record
if dType == 1:
    buff = struct.unpack(ibo+'i3fi', ifp.read(20))
else:
    buff = struct.unpack(ibo+'i3di', ifp.read(32))
pitch = (buff[1], buff[2], buff[3])

# time record
if dType == 1:
    buff = struct.unpack(ibo+'iifi', ifp.read(16))
else:
    buff = struct.unpack(ibo+'iqdi', ifp.read(24))
step, ftime = (buff[1], buff[2])


# open dstfile
ofp = open(dstf, "wb")

# write header
Sz = 8
ofp.write(struct.pack(obo+'4i', Sz, svType, dType, Sz))

# write size
if dType == 1:
    Sz = 12
    ofp.write(struct.pack(obo+'5i', Sz, dims[0], dims[1], dims[2], Sz))
else:
    Sz = 24
    ofp.write(struct.pack(obo+'i3qi', Sz, dims[0], dims[1], dims[2], Sz))

# write org
if dType == 1:
    Sz = 12
    ofp.write(struct.pack(obo+'i3fi', Sz, org[0], org[1], org[2], Sz))
else:
    Sz = 24
    ofp.write(struct.pack(obo+'i3di', Sz, org[0], org[1], org[2], Sz))

# write pitch
if dType == 1:
    Sz = 12
    ofp.write(struct.pack(obo+'i3fi', Sz, pitch[0], pitch[1], pitch[2], Sz))
else:
    Sz = 24
    ofp.write(struct.pack(obo+'i3di', Sz, pitch[0], pitch[1], pitch[2], Sz))

# write time
if dType == 1:
    Sz = 8
    ofp.write(struct.pack(obo+'iifi', Sz, step, ftime, Sz))
else:
    Sz = 16
    ofp.write(struct.pack(obo+'iqdi', Sz, step, ftime, Sz))

# write data
dimsIJV = dims[0] * dims[1] * vlen

buff = struct.unpack(ibo+'i', ifp.read(4))
Sz = buff[0]
ofp.write(struct.pack(obo+'i', Sz))
for k in range(0, dims[2]):
    # read/write a slice
    if dType == 1:
        for i in range(dimsIJV):
            slice = struct.unpack(ibo+'f', ifp.read(rlen))
            ofp.write(struct.pack(obo+'f', slice[0]))
    else:
        for i in range(dimsIJV):
            slice = struct.unpack(ibo+'d', ifp.read(rlen))
            ofp.write(struct.pack(obo+'d', slice[0]))

# read/write the last data
#ifp.read(4)
ofp.write(struct.pack(obo+'i', Sz))

ifp.close()
ofp.close()
