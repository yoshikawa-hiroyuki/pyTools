#! /usr/bin/env python
#
# scat2fdvParts
#

import sys
import struct
import numpy as np


def convert(srcf, dstf):
    # open srcf
    try:
        ifp = open(srcf, "r")
    except:
        print("open failed: %s" % srcf)
        return False

    # read head comment lines
    st = 0
    tm = 0.0
    line = ifp.readline()
    while line:
        if len(line) < 1:
            line = ifp.readline()
            continue
        if line[0] != '#': break
        if line.startswith('#TS'):
            toks = line[3:].split()
            try:
                st = int(toks[0])
                tm = float(toks[1])
            except:
                pass
        line = ifp.readline()
        continue # end of while(line)

    # parse np, nvar
    npts = 0
    nvar = 0
    toks = line.split()
    try:
        npts = int(toks[0])
        nvar = int(toks[1])
    except:
        print("can not get npts nor nvar: %s" % srcf)
        return False
    if npts < 1 or nvar < 1:
        print("invalid npts(%d) or nvar(%d)" % (npts, nvar))
        return False

    # open dstf
    try:
        ofp = open(dstf, "wb")
    except:
        print("open failed: %s" % dstf)
        return False

    # write header
    try:
        ofp.write(struct.pack('iiiiii', 4, 1, 4, 4, 0, 4))
    except:
        print("write header failed: %s" % dstf)
        return False

    # read data
    n = 0
    line = ifp.readline()
    pos_arr = np.ndarray((npts, 3), dtype=float)
    col_arr = np.ndarray((npts, 3), dtype=float)
    while line:
        toks = line.split()
        try:
            x = float(toks[0])
            y = float(toks[1])
            z = float(toks[2])
            for i in range(nvar):
                vals[i] = float(toks[i+3])
        except:
            line = ifp.readline()
            continue
        pos_arr[n,:] = [x, y, z]
        col_arr[n,:] = vals[-3:]
        n = n + 1
        if n >= npts:
            break
        line = ifp.readline()
        continue # end of while(line)

    # write npts, step, time
    try:
        ofp.write(struct.pack('iiiiifi', 4, npts, 4, 8, st, tm, 8))
    except:
        print("write time record failed: %s" % dstf)
        return False

    # write data
    vfmt = '%df' % nvar
    try:
        ofp.write(struct.pack('i', npts*3*4))
        for i in range(npts):
            ofp.write(struct.pack('3f', *pos_arr[i]))
        ofp.write(struct.pack('i', npts*3*4))

        ofp.write(struct.pack('i', npts*3*4))
        for i in range(npts):
            ofp.write(struct.pack('3f', *col_arr[i]))
        ofp.write(struct.pack('i', npts*3*4))        
    except:
        print("write data failed: %s" % dstf)
        return False
    
    # epilogue
    ifp.close()
    ofp.close()
    return True


def usage():
    print("usage: scat2fdvParts.py infile.scat outfile.pt")
    

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('-h', '--help'):
        usage()
        sys.exit(0)
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    if not convert(sys.argv[1], sys.argv[2]):
        sys.exit(1)

    sys.exit(0)
