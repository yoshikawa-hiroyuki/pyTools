#! /usr/bin/env python
#
# fixSvxFaceBC
#
import sys
import struct

def fixSvxFaceBC(in_f, out_f):
    # open input file
    try:
        ifp = open(in_f, "rb")
    except:
        print "open failed: %s" % in_f
        return False

    # open output file
    try:
        ofp = open(out_f, "wb")
    except:
        print "open failed: %s" % out_f
        ifp.close()
        return False

    # size record
    #ofp.write(ifp.read(20))
    buff = struct.unpack('5i', ifp.read(20))
    dims = [buff[1], buff[2], buff[3]]
    ofp.write(struct.pack('5i', buff[0], buff[1], buff[2], buff[3], buff[4]))

    # org record
    ofp.write(ifp.read(20))

    # pitch record
    ofp.write(ifp.read(20))

    # type record
    buff = struct.unpack('3i', ifp.read(12))
    dtype = buff[1]
    if dtype == 0: dtype = 31
    ofp.write(struct.pack('3i', buff[0], buff[1], buff[2]))

    # Volrate record
    if dtype & 1:
        buff = struct.unpack('i', ifp.read(4))
        sz = buff[0]
        ofp.write(struct.pack('i', buff[0]))
        ofp.write(ifp.read(sz))
        ofp.write(ifp.read(4))

    # Openrate record
    if dtype & 2:
        buff = struct.unpack('i', ifp.read(4))
        sz = buff[0]
        ofp.write(struct.pack('i', buff[0]))
        ofp.write(ifp.read(sz))
        ofp.write(ifp.read(4))

        buff = struct.unpack('i', ifp.read(4))
        sz = buff[0]
        ofp.write(struct.pack('i', buff[0]))
        ofp.write(ifp.read(sz))
        ofp.write(ifp.read(4))

        buff = struct.unpack('i', ifp.read(4))
        sz = buff[0]
        ofp.write(struct.pack('i', buff[0]))
        ofp.write(ifp.read(sz))
        ofp.write(ifp.read(4))

    # Medium record
    if dtype & 4:
        buff = struct.unpack('i', ifp.read(4))
        sz = buff[0]
        ofp.write(struct.pack('i', buff[0]))
        ofp.write(ifp.read(sz))
        ofp.write(ifp.read(4))

    # VoxBC record
    if dtype & 8:
        buff = struct.unpack('i', ifp.read(4))
        sz = buff[0]
        ofp.write(struct.pack('i', buff[0]))
        ofp.write(ifp.read(sz))
        ofp.write(ifp.read(4))

    # FaceBC record
    if dtype & 16:
        buff = struct.unpack('i', ifp.read(4))
        #sz = buff[0]
        sz = (dims[0]+1) * dims[1] * dims[2] * 4
        ofp.write(struct.pack('i', sz))
        ofp.write(ifp.read(sz))
        ifp.read(4)
        ofp.write(struct.pack('i', sz))

        buff = struct.unpack('i', ifp.read(4))
        #sz = buff[0]
        sz = dims[0] * (dims[1]+1) * dims[2] * 4
        ofp.write(struct.pack('i', sz))
        ofp.write(ifp.read(sz))
        ifp.read(4)
        ofp.write(struct.pack('i', sz))

        buff = struct.unpack('i', ifp.read(4))
        #sz = buff[0]
        sz = dims[0] * dims[1] * (dims[2]+1) * 4
        ofp.write(struct.pack('i', sz))
        ofp.write(ifp.read(sz))
        ifp.read(4)
        ofp.write(struct.pack('i', sz))

    ifp.close()
    ofp.close()
    return True


if __name__ == '__main__':
    in_f = ""
    out_f = ""
    if len(sys.argv) > 2:
        in_f = sys.argv[1]
        out_f = sys.argv[2]
    else:
        sys.exit("usage: %s  infile.svx  outfile.svx" % sys.argv[0])

    if not fixSvxFaceBC(in_f, out_f):
        sys.exit('fix failed.')
