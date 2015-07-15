#! /usr/bin/env python
#
# sbxinfo
#
"""report SBX file information
"""
import sys
import struct
import string
import zlib


def scanSbx(tgtf, forceAuxVal =-1):
    """ scan SBX file and report to stdout

        ARGS
          tgtf : path of SBX file to scan
          forceAuxVal : if non-negative, use this value as aux-record

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
    buff = struct.unpack('cccciiiiiiiq',
        ifp.read(struct.calcsize('cccciiiiiiiq')))
    if ( buff[0] != 'S' or buff[1] != 'B' or buff[2] != 'X' ):
        print "invalid file: not SBX"
        return -1
    
    dimension = buff[4]
    vlen = buff[5]
    dtype = buff[6]
    gc = buff[7]
    rlen = buff[8]
    crddef = buff[9]
    aux = buff[10]
    blksize = buff[11]
    
    if ( forceAuxVal >= 0 ):
        if ( forceAuxVal > 40 ):
            print "invalid aux value specified, ignore"
        else:
            aux = forceAuxVal
    
    print "dimension = ", dimension
    if ( dimension < 1 or dimension > 3 ):
        ifp.close()
        print "invalid dimension: %s" % dimension
        return -1
    
    print "vlen = ", vlen
    if ( vlen != 1 ):
        ifp.close()
        print "invalid vlen: != 1"
        return -1
    
    print "dtype = ", dtype
    if ( dtype != 1 and dtype != 2 and dtype != 4 ):
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

    print "aux = ", aux,
    d1bits = 0
    d2bits = 0
    d1mask = 0
    complexD = False
    if ( dtype == 1 ):
        if ( aux == 0 ):
            print "(simple 8bit data)"
        else:
            d2bits = aux & 15
            d1bits = 8 - d2bits
            auxUse = (aux >> 4) & 15
            useD1, useD2 = "used", "used"
            if auxUse == 1: useD2 = "unused"
            elif auxUse == 2: useD1 = "unused"
            print "(%s %dbit + %s %dbit complex data)" \
                  % (useD1, d1bits, useD2, d2bits)
            d1mask = 2**d1bits - 1
            complexD = True
    else:
        print "(not used)"
    
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
    buff = struct.unpack('qqq', ifp.read(24))
    dims = (buff[0], buff[1], buff[2])
    print "dims = ", dims
    
    # org record
    if ( rlen == 4 ):
        buff = struct.unpack('fff', ifp.read(12))
    else:
        buff = struct.unpack('ddd', ifp.read(24))
    org = (buff[0], buff[1], buff[2])
    print "org = ", org
    
    # pitch record
    if ( rlen == 4 ):
        buff = struct.unpack('fff', ifp.read(12))
    else:
        buff = struct.unpack('ddd', ifp.read(24))
    pitch = (buff[0], buff[1], buff[2])
    print "pitch = ", pitch
    
    
    # process data block
    print "scanning data record ...\r",
    sys.stdout.flush()
    dimSz = dims[0] * dims[1] * dims[2]
    if ( dtype == 1 ):
        packStr = 'B'
    elif ( dtype == 2 ):
        packStr = 'H'
    else:
        packStr = 'I'
    
    firstData = True
    
    buff = struct.unpack('q', ifp.read(8))
    zblkSz = buff[0]
    while ( zblkSz ):
        str = ifp.read(zblkSz)
        if ( blksize != 0 ):
            dstr = zlib.decompress(str)
            nelm = len(dstr)/dtype
            dfmt = "%d" % nelm + packStr
            vals = struct.unpack(dfmt, dstr)
        else:
            nelm = len(str)/dtype
            dfmt = "%d" % nelm + packStr
            vals = struct.unpack(dfmt, str)
            
        if ( firstData ):
            if ( complexD ):
                minR = vals[0] & d1mask
                maxR = vals[0] & d1mask
                minV = vals[0] >> d1bits
                maxV = vals[0] >> d1bits
            else:
                minV = vals[0]
                maxV = vals[0]
            firstData = False
        if ( complexD ):
            for i in range(0, nelm):
                volrate = vals[i] & d1mask
                if ( minR > volrate ):
                    minR = volrate
                elif ( maxR < volrate ):
                    maxR = volrate
                medium = vals[i] >> d1bits
                if ( minV >medium ):
                    minV = medium
                elif ( maxV < medium ):
                    maxV = medium
        else:
            for i in range(0, nelm):
                if ( minV > vals[i] ):
                    minV = vals[i]
                elif ( maxV < vals[i] ):
                    maxV = vals[i]
    
        buff = struct.unpack('q', ifp.read(8))
        zblkSz = buff[0]
    
    if ( complexD ):
        print "data0(%dbit) min = " % d1bits, minR, ", max = ", maxR
    print "data1 min = ", minV, ", max = ", maxV
    
    
    # optional record
    try:
        buff = struct.unpack('qqqqqq', ifp.read(48))
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
        sys.exit("usage: %s targetfile.sbx [auxval]" % sys.argv[0])
    
    forceAuxVal = -1
    if ( len(sys.argv) > 2 ):
        forceAuxVal = string.atoi(sys.argv[2])

    scanSbx(tgtf, forceAuxVal)

