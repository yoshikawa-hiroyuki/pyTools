#! /usr/bin/env python
#
# fdvParts2Lines
#
"""converts 4DVis Particle data file to Lines file
     using numpy.array
"""
import sys
import struct
import numpy

def convert(srcf, dstf, shdf):
    # open files
    try:
        ifp = open(srcf, "rb")
    except:
        print("open failed: %s" % srcf)
        return -1
    try:
        ofp = open(dstf, "wb")
    except:
        print("open failed: %s" % dstf)
        ifp.close()
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

    ofp.write(struct.pack('6i', 4, 3, 4, 4, 0, 4)) # MODE=3
    
    od0 = numpy.array(0, dtype=float)
    
    # step loop
    stp = 0
    while True:
        # time record
        try:
            buff = struct.unpack(bo+'5ifi', ifp.read(28))
        except:
            break # eof
        
        pnum  = buff[1]
        istep = buff[4]
        ftime = buff[5]
        if pnum < 1:
            continue
    
        print('%d : step=%d, pnum=%d' % (stp, istep, pnum))

        if stp == 0:
            try:
                data = numpy.array(0, dtype=float)
                data.resize((pnum, 3+vlen))
            except:
                print("memory allocation failed")
                ifp.close()
                ofp.close()
                return -1
    
        # particle record
        ifp.read(4)
        for i in range(0, pnum):
            buff = struct.unpack(bo+'3f', ifp.read(12))
            data[i,0:3] = buff[0:3]
        ifp.read(4)
    
        # attrib record
        if vlen != 0:
            ifp.read(4)
            if vlen == 3:
                for i in range(0, pnum):
                    buff = struct.unpack(bo+'3f', ifp.read(12))
                    data[i,3:6] = buff[0:3]
            elif vlen == 1:
                for i in range(0, pnum):
                    data[i,3] = struct.unpack(bo+'i', ifp.read(4))
            ifp.read(4)

        # alloc od
        #import pdb; pdb.set_trace()
        try:
            od = numpy.array(0, dtype=float)
            od.resize((stp+1, pnum*3))
        except:
            print("memory allocation failed")
            ifp.close()
            ofp.close()
            return -1
        for s in range(stp):
            od[s, 0:pnum*3] = od0[s, 0:pnum*3]
        for i in range(pnum):
            od[stp, i*3  ] = data[i,0]
            od[stp, i*3+1] = data[i,1]
            od[stp, i*3+2] = data[i,2]

        # write data
        ofp.write(struct.pack('iiiiifi', 4, pnum, 4, 8, istep, ftime, 8))
        for i in range(0, pnum):
            ofp.write(struct.pack('iiii', 4, stp+1, 4, pnum*12))
            for s in range(stp+1):
                ofp.write(struct.pack('fff', od[s, i*3],
                                      od[s, i*3+1], od[s, i*3+2]))
            ofp.write(struct.pack('iiii', pnum*12, 4, i, 4))

        od0 = od
        stp = stp + 1
        continue
    
    ifp.close()
    ofp.close()

    # shdf
    try:
        sfp = open(shdf, 'w')
        for i in range(pnum):
            if float(i/2) == float(i)/2.0:
                sfp.write('0.5 0.5 0.5  1.0 0.5 0.5  0.5 0.5 0.5  100 0\n')
            else:
                sfp.write('0.5 0.5 0.5  0.5 0.5 1.0  0.5 0.5 0.5  100 0\n')
        sfp.close()
    except:
        passs

    return 0
    

if __name__ == '__main__':
    srcf = ""
    dstf = ""
    shdf = ""
    if len(sys.argv) > 1 and sys.argv[1] == '-h':
        sys.exit("usage: %s srcfile.pt dstfile.lin [shadf]" % sys.argv[0])

    if ( len(sys.argv) > 2 ):
        srcf = sys.argv[1]
        dstf = sys.argv[2]
        if ( len(sys.argv) > 3 ):
            shdf = sys.argv[3]
    else:
        sys.exit("usage: %s srcfile.pt dstfile.lin [shadf]" % sys.argv[0])

    ret = convert(srcf, dstf, shdf)

