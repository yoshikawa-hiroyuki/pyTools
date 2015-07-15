#! /usr/bin/env python
#
# spxinfo
#
"""report SPX file information
"""
import sys
import struct
import string
import zlib


def scanSpx(tgtf):
    """ scan SPX file and report to stdout

        ARGS
          tgtf : path of SPX file to scan

        RETURNS
          0 : succeed
          -1 : failed
    """
    # open file
    try:
        ifp = open(tgtf, "rb")
    except:
        print "open failed: %s" % tgtf
        return -1
    
    # attribute record
    bo = '<'
    header = ifp.read(struct.calcsize('cccciiiiiiiq'))
    buff = struct.unpack(bo+'cccciiiiiiiq', header)
    if ( buff[0] != 'S' or buff[1] != 'P' or buff[2] != 'X' ):
        print "invalid file: not SPX"
        return -1
    if buff[4] != 1 and buff[4] != 2 and buff[4] != 3:
        bo = '>'
        buff = struct.unpack(bo+'cccciiiiiiiq', header)
        if buff[4] != 1 and buff[4] != 2 and buff[4] != 3:
            print "invalid dimension, not 1, 2, nor 3"
            return -1
    dimension = buff[4]
    vlen = buff[5]
    dtype = buff[6]
    gc = buff[7]
    rlen = buff[8]
    crddef = buff[9]
    aux = buff[10]
    blksize = buff[11]
    if bo == '<':
        print "endian = little"
    else:
        print "endian = big"
    print "dimension = ", dimension
    if ( dimension < 1 or dimension > 3 ):
        ifp.close()
        print "invalid dimension: %s" % dimension
        return -1
    
    print "vlen = ", vlen
    if ( vlen != 1 and vlen != 3 ):
        ifp.close()
        print "invalid vlen: != 1"
        return -1
    
    print "dtype = ", dtype
    if ( dtype != 1 and dtype != 3 ):
        ifp.close()
        print "invalid dtype"
        return -1
    
    print "gc = ", gc
    
    print "rlen = ", rlen,
    if ( rlen == 4 ):
        print "(single precision)"
    elif ( rlen == 8 ):
        print "(double precision)"
    else:
        ifp.close()
        print "invalid rlen"
        return -1
    
    print "crddef = ", crddef,
    if ( crddef == 1 ):
        print "(regular)"
    elif ( crddef == 2 ):
        print "(collocate)"
    elif ( crddef == 3 ):
        print "(staggered 1)"
    elif ( crddef == 4 ):
        print "(staggered 2)"
    else:
        ifp.close()
        print "invalid crddef: unknown type"
        return -1

    print "aux = ", aux

    print "blksize = ", blksize,
    if ( blksize == 0 ):
        print "(uncompressed)"
    elif ( blksize > 0 ):
        print "(compressed)"
    else:
        ifp.close()
        print "invalid blksize"
        return -1
    
    # size record
    buff = struct.unpack(bo+'qqq', ifp.read(24))
    dims = (buff[0], buff[1], buff[2])
    print "dims = ", dims
    
    # org record
    if ( rlen == 4 ):
        buff = struct.unpack(bo+'fff', ifp.read(12))
    else:
        buff = struct.unpack(bo+'ddd', ifp.read(24))
    org = (buff[0], buff[1], buff[2])
    print "org = ", org
    
    # pitch record
    if ( rlen == 4 ):
        buff = struct.unpack(bo+'fff', ifp.read(12))
    else:
        buff = struct.unpack(bo+'ddd', ifp.read(24))
    pitch = (buff[0], buff[1], buff[2])
    print "pitch = ", pitch

    # time record
    if ( rlen == 4 ):
        buff = struct.unpack(bo+'qf', ifp.read(12))
    else:
        buff = struct.unpack(bo+'qd', ifp.read(16))
    istep = buff[0]
    ftime = buff[1]
    print "step = ", istep, "time = ", ftime
    
    # process data block
    print "scanning data record ...\r",
    sys.stdout.flush()
    dimSz = dims[0] * dims[1] * dims[2]
    if ( rlen == 4 ):
        packStr = 'f'
    else:
        packStr = 'd'
    
    firstData = True
    minV = {}
    maxV = {}
    buff = struct.unpack(bo+'q', ifp.read(8))
    if ( blksize != 0 ):
        ### COMPRESSED DATA ###
        nelm = blksize
        ssz = nelm * vlen
        zblkSz = buff[0]
        while ( zblkSz ):
            str = ifp.read(zblkSz)
            dstr = zlib.decompress(str)
            dfmt = '%d' % ssz + packStr
            vals = struct.unpack(bo+dfmt, dstr)

            if ( firstData ):
                for i in range(0, vlen):
                    minV[i] = vals[i]
                    maxV[i] = vals[i]
                firstData = False

            vidx = 0
            for l in range(nelm):
                for i in range(0, vlen):
                    if ( minV[i] > vals[vidx] ):
                        minV[i] = vals[vidx]
                    elif ( maxV[i] < vals[vidx] ):
                        maxV[i] = vals[vidx]
                    vidx = vidx + 1

            buff = struct.unpack(bo+'q', ifp.read(8))
            zblkSz = buff[0]
    else:
        ### UNCOMPRESSED DATA ###
        dsz = vlen * rlen
        for l in range(dimSz):
            str = ifp.read(dsz)
            dfmt = "%d" % vlen + packStr
            vals = struct.unpack(bo+dfmt, str)
            if ( firstData ):
                for i in range(0, vlen):
                    minV[i] = vals[i]
                    maxV[i] = vals[i]
                firstData = False
            for i in range(0, vlen):
                if ( minV[i] > vals[i] ):
                    minV[i] = vals[i]
                elif ( maxV[i] < vals[i] ):
                    maxV[i] = vals[i]
        buff = struct.unpack(bo+'q', ifp.read(8))

    # print min/max value(s)
    for i in range(vlen):
        print "data(%d) min = " % i, minV[i], ", max = ", maxV[i]
    
    
    # optional record
    try:
        buff = struct.unpack(bo+'qqqqqq', ifp.read(48))
    except:
        ifp.close()
        print "no optional data"
        return 0
    
    wdims = (buff[0], buff[1], buff[2])
    staidx = (buff[3], buff[4], buff[5])
    print "wdims = ", wdims
    print "start = ", staidx
    
    ifp.close()
    return 0


if __name__ == '__main__':
    tgtf = ""
    if ( len(sys.argv) > 1 ):
        tgtf = sys.argv[1]
    else:
        sys.exit("usage: %s targetfile.spx" % sys.argv[0])
    
    scanSpx(tgtf)

