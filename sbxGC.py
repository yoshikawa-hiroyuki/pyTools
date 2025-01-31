#! /usr/bin/env python
#
# sbxGC
#
"""replace gc record of SBX file
"""
import sys
import struct
import string


def replaceSbxGC(in_f, out_f, ngc):
    """ replace gc record of SBX file and save

        ARGS
          in_f : path of input SBX file
          out_f : path of output SBX file
          ngc : new gc value

        RETURNS
          0 : succeed
          -1 : failed
    """
    if not ngc:
        print("invalid ngc value")
        return -1

    # open input file
    try:
        ifp = open(in_f, "rb")
    except:
        print("open failed: %s" % in_f)
        return -1

    # attribute record
    buff = struct.unpack('cccciiiiiiiq', ifp.read(40))
    if ( buff[0] != 'S' or buff[1] != 'B' or buff[2] != 'X' ):
        print("invalid file: not SBX")
        return -1
    
    dimension = buff[4]
    vlen = buff[5]
    dtype = buff[6]
    gc = buff[7]
    rlen = buff[8]
    crddef = buff[9]
    aux = buff[10]
    blksize = buff[11]
    
    if ( dimension < 1 or dimension > 3 ):
        ifp.close()
        print("invalid dimension: %s" % dimension)
        return -1
    
    if ( vlen != 1 ):
        ifp.close()
        print("invalid vlen: %d (!= 1)" % vlen)
        return -1
    
    if ( dtype != 1 and dtype != 2 and dtype != 4 ):
        ifp.close()
        print("invalid dtype: %d" % dtype)
        return -1
    
    if ( rlen != 4 and rlen != 8 ):
        ifp.close()
        print("invalid rlen: %d" % rlen)
        return -1
    
    if ( crddef < 1 or crddef > 4 ):
        ifp.close()
        print("invalid crddef: %d" % crddef)
        return -1
    
    if ( gc == ngc ):
        ifp.close()
        print("gc == %d, no need to convert" % ngc)
        return -1
    else:
        print("set gc to %d (old value = %d)" % (ngc, gc))
        gc = ngc
    
    if ( blksize < 0 ):
        ifp.close()
        print("invalid blksize: %d" % blksize)
        return -1
    
    # open output file
    try:
        ofp = open(out_f, "wb")
    except:
        print("open failed: %s" % out_f)
        ifp.close()
        return -1
    
    # write header
    ofp.write(struct.pack('4siiiiiiiq', 'SBX', dimension,
                          vlen, dtype, gc, rlen, crddef, aux, blksize))
    
    # size record
    ofp.write(ifp.read(24))
    
    # org record
    if ( rlen == 4 ):
        ofp.write(ifp.read(12))
    else:
        ofp.write(ifp.read(24))
    
    # pitch record
    if ( rlen == 4 ):
        ofp.write(ifp.read(12))
    else:
        ofp.write(ifp.read(24))
    
    # process data block
    buff = struct.unpack('q', ifp.read(8))
    zblkSz = buff[0]
    ofp.write(struct.pack('q', zblkSz))
    while ( zblkSz ):
        ofp.write(ifp.read(zblkSz))
        buff = struct.unpack('q', ifp.read(8))
        zblkSz = buff[0]
        ofp.write(struct.pack('q', zblkSz))
    
    # optional record
    try:
        ofp.write(ifp.read(48))
    except:
        pass
    
    ifp.close()
    print("conversion done")
    return 0


if __name__ == '__main__':
    in_f = ""
    out_f = ""
    forceGC = None
    if ( len(sys.argv) > 3 ):
        in_f = sys.argv[1]
        out_f = sys.argv[2]
        forceGC = string.atoi(sys.argv[3])
    else:
        sys.exit("usage: %s infile.sbx outfile.sbx gcval" % sys.argv[0])
    
    ret = replaceSbxGC(in_f, out_f, forceGC)
    sys.exit("done")
