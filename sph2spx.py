#! /usr/bin/env python
#
# sph2spx
#
import sys
import struct
import string
import zlib

srcf = ""
dstf = ""
zip = False
if len(sys.argv) > 2:
    srcf = sys.argv[1]
    dstf = sys.argv[2]
    if len(sys.argv) > 3 and sys.argv[3] == 'zip':
        zip = True
else:
    sys.exit("usage: %s srcfile.sph dstfile.spx [zip]" % sys.argv[0])

# open srcfile
ifp = open(srcf, "rb")

# attribure record
bo = '<'
ispx = 4739155 # 'SPX\0' in little endian
header = ifp.read(16)
buff = struct.unpack(bo+'4i', header)
svType = buff[1]
dType = buff[2]
if svType != 1 and svType != 2:
    bo = '>'
    ispx = 1397774336 # 'SPX\0' in big endian
    buff = struct.unpack(bo+'iiii', header)
    svType = buff[1]
    dType = buff[2]
    if svType != 1 and svType != 2:
        print "invalid svType: not 1 nor 2"
        sys.exit(-1)
if dType != 1 and dType != 2:
    print "invalid dType: not 1 nor 2"
    sys.exit(-1)

# size record
if dType == 1:
    buff = struct.unpack(bo+'5i', ifp.read(20))
else:
    buff = struct.unpack(bo+'i3qi', ifp.read(32))
dims = (buff[1], buff[2], buff[3])
dimSz = dims[0] * dims[1] * dims[2]
if dimSz < 1:
    print "invalid dims: %d x %d x %d" % (dims[0], dims[1], dims[2])
    sys.exit(-1)

# org record
if dType == 1:
    buff = struct.unpack(bo+'i3fi', ifp.read(20))
else:
    buff = struct.unpack(bo+'i3di', ifp.read(32))
org = (buff[1], buff[2], buff[3])

# pitch record
if dType == 1:
    buff = struct.unpack(bo+'i3fi', ifp.read(20))
else:
    buff = struct.unpack(bo+'i3di', ifp.read(32))
pitch = (buff[1], buff[2], buff[3])

# time record
if dType == 1:
    buff = struct.unpack(bo+'iifi', ifp.read(16))
else:
    buff = struct.unpack(bo+'iqdi', ifp.read(24))
step, ftime = (buff[1], buff[2])


# open dstfile
ofp = open(dstf, "wb")

# write header
if svType == 1:
    vlen = 1
    dtype = 1
else:
    vlen = 3
    dtype = 3
gc = 0
if dType == 1:
    rlen = 4
else:
    rlen = 8
crddef = 1
aux = 0
if zip:
    blksize = dims[0] * dims[1]  ## * vlen * rlen
else:
    blksize = 0
ofp.write(struct.pack('@i', ispx))
ofp.write(struct.pack(bo+'iiiiiiiq', 3,
                      vlen, dtype, gc, rlen, crddef, aux, blksize))
print 'dimension=3'
print 'vlen=', vlen
print 'dtype=', dtype
print 'gc=', gc
print 'rlen=', rlen
print 'crddef=', crddef
print 'aux=', aux
print 'blksize=', blksize

# write size
ofp.write(struct.pack(bo+'qqq', dims[0], dims[1], dims[2]))
print 'dims=', dims

# write org
if rlen == 4:
    ofp.write(struct.pack(bo+'fff', org[0], org[1], org[2]))
else:
    ofp.write(struct.pack(bo+'ddd', org[0], org[1], org[2]))
print 'org=', org

# write pitch
if rlen == 4:
    ofp.write(struct.pack(bo+'fff', pitch[0], pitch[1], pitch[2]))
else:
    ofp.write(struct.pack(bo+'ddd', pitch[0], pitch[1], pitch[2]))
print 'pitch=', pitch

# write time
if rlen == 4:
    ofp.write(struct.pack(bo+'qf', step, ftime))
else:
    ofp.write(struct.pack(bo+'qd', step, ftime))
print 'step=%d, time=%f' % (step, ftime)

# write data
dimsIJV = dims[0] * dims[1] * vlen

ifp.read(4)
if zip:
    for k in range(0, dims[2]):
        # read a block(slice)
        slice = ifp.read(dimsIJV * rlen)
        # compress
        cmpData = zlib.compress(slice)
        # write
        ofp.write(struct.pack(bo+'q', len(cmpData)))
        ofp.write(cmpData)
else:
    dataSz = dims[0] * dims[1] * dims[2] * vlen * rlen
    ofp.write(struct.pack(bo+'q', dataSz))
    for k in range(0, dims[2]):
        # read a slice
        slice = ifp.read(dimsIJV * rlen)
        # write
        ofp.write(slice)
        

# read/write the last data
ifp.read(4)
ofp.write(struct.pack(bo+'q', 0))

ifp.close()
ofp.close()
