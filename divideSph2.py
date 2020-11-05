#! /usr/bin/env python
#
import os, sys
import struct

def divideSph(div, sphPath, outDir ='.'):
    if div < 2 :
        print "invalid div: ", div
        return False

    #------------- load sph file -------------
    # open file
    try:
        ifp = open(sphPath, "rb")
    except:
        print "open failed: %s" % sphPath
        return False

    # attribure record
    buff = struct.unpack('4i', ifp.read(16))
    svType = buff[1]
    dType = buff[2]
    if svType != 1 and svType != 2:
        print "invalid svType: not 1 nor 2"
        return False
    if dType != 1 and dType != 2:
        print "invalid dType: not 1 nor 2"
        return False

    if svType == 1:
        vlen = 1
        dtype = 1
    else:
        vlen = 3
        dtype = 3
    if dType == 1:
        rlen = 4
    else:
        rlen = 8

    # size record
    if dType == 1:
        buff = struct.unpack('5i', ifp.read(20))
    else:
        buff = struct.unpack('i3qi', ifp.read(32))
    dims = (buff[1], buff[2], buff[3])
    dimSz = dims[0] * dims[1] * dims[2]
    if dimSz < 1:
        print "invalid dims: %d x %d x %d" % (dims[0], dims[1], dims[2])
        return False

    # org record
    if dType == 1:
        buff = struct.unpack('i3fi', ifp.read(20))
    else:
        buff = struct.unpack('i3di', ifp.read(32))
    org = (buff[1], buff[2], buff[3])

    # pitch record
    if dType == 1:
        buff = struct.unpack('i3fi', ifp.read(20))
    else:
        buff = struct.unpack('i3di', ifp.read(32))
    pitch = (buff[1], buff[2], buff[3])

    # time record
    if dType == 1:
        buff = struct.unpack('iifi', ifp.read(16))
    else:
        buff = struct.unpack('iqdi', ifp.read(24))
    step, ftime = (buff[1], buff[2])

    # data record
    dimsIJV = dims[0] * dims[1] * vlen
    if ( rlen == 4 ):
        packStr = '%df' % dimsIJV
    elif ( rlen == 8 ):
        packStr = '%dd' % dimsIJV
    ifp.read(4)
    #dataWhole = struct.unpack(packStr, ifp.read(dimsIJKV * rlen))
    #ifp.read(4)
    #ifp.close()

    #------------- divide loop -------------
    fileIdx = 0
    base_path = sphPath[0:-4]
    if outDir != '.':
        xdir = os.path.dirname(base_path)
        xbase = os.path.basename(base_path)
        base_path = os.path.join(outDir, xbase)
        if not os.path.exists(outDir):
            os.makedirs(outDir)

    newDims = [dims[0], dims[1], dims[2] / div]
    newOrg = [org[0], org[1], org[2]]
    newOrgIdx = [0, 0, 0]
    
    for k in range(div):
        if k == div -1 :
            newDims[2] = dims[2] - newDims[2] * k

        newPath = base_path + '_%04d.sph' % fileIdx
        print 'newPath=', newPath
        print 'newDims=', newDims
        print 'newOrg=', newOrg
        print 'newOrgIdx=', newOrgIdx

        # write sph file
        ofp = open(newPath, 'wb')
        ofp.write(struct.pack('4i', 8, svType, dType, 8))
        if dType == 1:
            ofp.write(struct.pack('5i', 12, newDims[0],
                                  newDims[1], newDims[2], 12))
        else:
            ofp.write(struct.pack('i3qi', 24, newDims[0],
                                  newDims[1], newDims[2], 24))
        if dType == 1:
            ofp.write(struct.pack('i3fi', 12, newOrg[0],
                                  newOrg[1], newOrg[2], 12))
        else:
            ofp.write(struct.pack('i3di', 24, newOrg[0],
                                  newOrg[1], newOrg[2], 24))
        if dType == 1:
            ofp.write(struct.pack('i3fi', 12, pitch[0],
                                  pitch[1], pitch[2], 12))
        else:
            ofp.write(struct.pack('i3di', 24, pitch[0],
                                  pitch[1], pitch[2], 24))
        if dType == 1:
            ofp.write(struct.pack('iifi', 8, step, ftime, 8))
        else:
            ofp.write(struct.pack('iqdi', 16, step, ftime, 16))

        newSz = newDims[0] * newDims[1] * newDims[2] * 4
        if svType != 1: newSz = newSz * 3
        if dType == 2: newSz = newSz * 2
        ofp.write(struct.pack('i', newSz))

        if ( rlen == 4 ):
            packStr = '%df' % dimsIJV
        elif ( rlen == 8 ):
            packStr = '%dd' % dimsIJV

        for kk in range(newOrgIdx[2], newOrgIdx[2] +newDims[2]):
            st_idx = dimsIJV * kk
            ed_idx = st_idx + dimsIJV

            dataSlice = struct.unpack(packStr, ifp.read(dimsIJV * rlen))
            ofp.write(struct.pack(packStr, *dataSlice[:]))

        ofp.write(struct.pack('i', newSz))
        ofp.close()
        fileIdx += 1

        newOrg[2] += pitch[2] * newDims[2]
        newOrgIdx[2] += newDims[2]

    ifp.close()
    return True



if __name__ == '__main__':
    div = 1
    tgtf = ''
    odir = '.'
    if len(sys.argv) > 2:
        div = int(sys.argv[1])
        tgtf = sys.argv[2]
        if len(sys.argv) > 3:
            odir = sys.argv[3]
    else:
        sys.exit("usage: %s div targetfile.sph [outdir]" \
                     % sys.argv[0])

    ret = divideSph(div, tgtf, odir)
    if not ret:
        sys.exit(1)
    sys.exit(0)
