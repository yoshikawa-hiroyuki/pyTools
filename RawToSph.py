#! /usr/bin/env python
import sys
import struct

def convert(dims, srcf, dstf, pitch=None):
    # check dims
    try:
        dimSz = dims[0] * dims[1] * dims[2]
        if dimSz < 1:
            print("invalid dim size")
            return -1
    except:
        print("invalid dim size")
        return -1

    # open srcfile
    try:
        ifp = open(srcf, "rb")
    except:
        print("open failed: %s" % srcf)
        return -1
    
    # open dstf
    try:
        ofp = open(dstf, "wb")
    except:
        print("open failed: %s" % dstf)
        ifp.close
        return -1

    # write header
    sz = 8
    svType = 1 # scalar
    dType = 1 # single precision
    ofp.write(struct.pack('4i', sz, svType, dType, sz))

    sz = 12
    ofp.write(struct.pack('5i', sz, dims[0], dims[1], dims[2], sz))

    sz = 12
    org = [0.0, 0.0, 0.0]
    ofp.write(struct.pack('i3fi', sz, org[0], org[1], org[2], sz))

    sz = 12
    try:
        if pitch[0] <= 0.0 or pitch[1] <= 0.0 or pitch[2] <= 0.0:
            pit = [1.0, 1.0, 1.0]
        else:
            pit = pitch
    except:
        pit = [1.0, 1.0, 1.0]
    ofp.write(struct.pack('i3fi', sz, pit[0], pit[1], pit[2], sz))

    sz = 8
    ofp.write(struct.pack('iifi', sz, 0, 0.0, sz))

    # convert data
    ofp.write(struct.pack('I', dimSz * 4))
    slSz = dims[0] * dims[1]
    fmt = '%d' % slSz + 'B'
    try:
        for z in range(dims[2]):
            slice = struct.unpack(fmt, ifp.read(slSz))
            for i in range(slSz):
                ofp.write(struct.pack('f', slice[i]))
    except:
        print('conversion failed')
        ifp.close()
        ofp.close()
        return -1
    ofp.write(struct.pack('I', dimSz * 4))

    ifp.close()
    ofp.close()
    return 0


def usage():
    print('usage: RawToSph.py infile.raw outfile.sph IMAX JMAX KMAX [px py pz]')


if __name__ == '__main__':
    if len(sys.argv) < 6:
        usage()
        sys.exit(-1)

    try:
        dims = [int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])]
    except:
        print('invalid args')
        sys.exit(-1)

    pit = None
    if len(sys.argv) >= 9:
        try:
            pit = [float(sys.argv[6]), float(sys.argv[7]), float(sys.argv[8])]
        except:
            print('invalid args')
            sys.exit(-1)
    
    ret = convert(dims, sys.argv[1], sys.argv[2], pit)
    if ret < 0:
        sys.exit(-1)
    sys.exit(0)
