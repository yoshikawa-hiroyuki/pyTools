#! /usr/bin/env python
#
# fdvParts2scats
#
"""converts 4DVis Particle data file to V-Isio SCAT files
     converts only XYZ of points, ignores color indices.
"""
import sys
import struct


def convert(srcf, dstf_base):
    """ converts 4DVis Particle data file to V-Isio SCAT files
        ARGS
          srcf : path of source 4DVis Particle data file
          dstf_base : basename of V-Isio SCAT files
        RETURNS
          0 : succeed
          -1 : failed
    """
    
    # open srcfile
    try:
        ifp = open(srcf, "rb")
    except:
        print("open failed: %s" % srcf)
        return -1
    
    # header record
    bo = '@'
    buff = struct.unpack('i', ifp.read(4))
    if buff[0] != 4:
        if sys.byteorder == 'little': bo = '>'
        else: bo = '<'
    
    buff = struct.unpack(bo+'5i', ifp.read(20))
    mode = buff[0]
    vlen = 0
    if mode == 1 or mode == 2: vlen = 3
    elif mode == 3 or mode == 4: vlen = 1
    
    # step loop
    stp = 0
    while True:
        # time record
        try:
            buff = struct.unpack(bo+'5ifi', ifp.read(28))
        except:
            break #eof
        
        pnum  = buff[1]
        istep = buff[4]
        ftime = buff[5]
        if pnum < 1:
            continue
    
        print('%d : step=%d, pnum=%d' % (stp, istep, pnum))
    
        # open dstfile
        dstf = dstf_base + '_%08d.scat' % istep
        try:
            ofp = open(dstf, "w")
        except:
            print("open failed: %s" % dstf)
            return -1
        ofp.write('# %s generated\n' % sys.argv[0])
        ofp.write('#TS %d %f\n' % (istep, ftime))
        ofp.write('%d 1\n' % pnum)
    
        # particle record
        ifp.read(4)
        for i in range(0, pnum):
            buff = struct.unpack(bo+'3f', ifp.read(12))
            ofp.write('%f %f %f %d\n' % (buff[0], buff[1], buff[2], i))
        ifp.read(4)
    
        ofp.close()
    
        # skip attrib record
        if vlen != 0:
            ifp.read(4)
            ifp.seek(4 * pnum * vlen)
            ifp.read(4)
    
        stp = stp + 1
        continue
    
    ifp.close()
    return 0


if __name__ == '__main__':
    srcf = ""
    dstf_base = ""
    if ( len(sys.argv) > 2 ):
        srcf = sys.argv[1]
        dstf_base = sys.argv[2]
    else:
        sys.exit("usage: %s srcfile.pt dstfile_base" % sys.argv[0])

    ret = convert(srcf, dstf_base)
