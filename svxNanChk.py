#! /usr/bin/env python
#
# svxNanChk
#
import sys
import struct

def svxNanChk(in_f, out_f, alt=0.0):
    ialt = int(alt)

    # open input file
    try:
        ifp = open(in_f, "rb")
    except:
        print("open failed: %s" % in_f)
        return False

    # open output file
    try:
        ofp = open(out_f, "wb")
    except:
        print("open failed: %s" % out_f)
        ifp.close()
        return False

    # size record
    buff = struct.unpack('5i', ifp.read(20))
    dims = (buff[1], buff[2], buff[3])
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
        sz = buff[0] / 4
        ofp.write(struct.pack('i', buff[0]))
        nanFound = False
        for i in xrange(0, sz):
            vals = struct.unpack('f', ifp.read(4))
            if vals[0] != vals[0]:
                nanFound = True
                x = alt
            else:
                x = vals[0]
            ofp.write(struct.pack('f', x))
        ofp.write(ifp.read(4))
        if nanFound:
            print("\rVolRate NaN found.")

    # Openrate record
    if dtype & 2:
        buff = struct.unpack('i', ifp.read(4))
        sz = buff[0] / 4
        ofp.write(struct.pack('i', buff[0]))
        nanFound = False
        for i in xrange(0, sz):
            vals = struct.unpack('f', ifp.read(4))
            if vals[0] != vals[0]:
                nanFound = True
                x = alt
            else:
                x = vals[0]
            ofp.write(struct.pack('f', x))
        ofp.write(ifp.read(4))
        if nanFound:
            print("\rOpenRate[X] NaN found."        )

        buff = struct.unpack('i', ifp.read(4))
        sz = buff[0] / 4
        ofp.write(struct.pack('i', buff[0]))
        nanFound = False
        for i in xrange(0, sz):
            vals = struct.unpack('f', ifp.read(4))
            if vals[0] != vals[0]:
                nanFound = True
                x = alt
            else:
                x = vals[0]
            ofp.write(struct.pack('f', x))
        ofp.write(ifp.read(4))
        if nanFound:
            print("\rOpenRate[Y] NaN found.")

        buff = struct.unpack('i', ifp.read(4))
        sz = buff[0] / 4
        ofp.write(struct.pack('i', buff[0]))
        nanFound = False
        for i in xrange(0, sz):
            vals = struct.unpack('f', ifp.read(4))
            if vals[0] != vals[0]:
                nanFound = True
                x = alt
            else:
                x = vals[0]
            ofp.write(struct.pack('f', x))
        ofp.write(ifp.read(4))
        if nanFound:
            print("\rOpenRate[Z] NaN found.")

    # Medium record
    if dtype & 4:
        buff = struct.unpack('i', ifp.read(4))
        sz = buff[0] / 4
        ofp.write(struct.pack('i', buff[0]))
        nanFound = False
        for i in xrange(0, sz):
            vals = struct.unpack('i', ifp.read(4))
            if vals[0] != vals[0]:
                nanFound = True
                x = ialt
            else:
                x = vals[0]
            ofp.write(struct.pack('i', x))
        ofp.write(ifp.read(4))
        if nanFound:
            print("\rMedium NaN found.")

    # VoxBC record
    if dtype & 8:
        buff = struct.unpack('i', ifp.read(4))
        sz = buff[0] / 4
        ofp.write(struct.pack('i', buff[0]))
        nanFound = False
        for i in xrange(0, sz):
            vals = struct.unpack('i', ifp.read(4))
            if vals[0] != vals[0]:
                nanFound = True
                x = ialt
            else:
                x = vals[0]
            ofp.write(struct.pack('i', x))
        ofp.write(ifp.read(4))
        if nanFound:
            print("\rVoxBC NaN found.")

    # FaceBC record
    if dtype & 16:
        buff = struct.unpack('i', ifp.read(4))
        sz = buff[0] / 4
        ofp.write(struct.pack('i', buff[0]))
        nanFound = False
        for i in xrange(0, sz):
            vals = struct.unpack('i', ifp.read(4))
            if vals[0] != vals[0]:
                nanFound = True
                x = ialt
            else:
                x = vals[0]
            ofp.write(struct.pack('i', x))
        ofp.write(ifp.read(4))
        if nanFound:
            print("\rFaceBC[X] NaN found.")

        buff = struct.unpack('i', ifp.read(4))
        sz = buff[0] / 4
        ofp.write(struct.pack('i', buff[0]))
        nanFound = False
        for i in xrange(0, sz):
            vals = struct.unpack('i', ifp.read(4))
            if vals[0] != vals[0]:
                nanFound = True
                x = ialt
            else:
                x = vals[0]
            ofp.write(struct.pack('i', x))
        ofp.write(ifp.read(4))
        if nanFound:
            print("\rFaceBC[Y] NaN found.")

        buff = struct.unpack('i', ifp.read(4))
        sz = buff[0] / 4
        ofp.write(struct.pack('i', buff[0]))
        nanFound = False
        for i in xrange(0, sz):
            vals = struct.unpack('i', ifp.read(4))
            if vals[0] != vals[0]:
                nanFound = True
                x = ialt
            else:
                x = vals[0]
            ofp.write(struct.pack('i', x))
        ofp.write(ifp.read(4))
        if nanFound:
            print("\rFaceBC[Z] NaN found.")

    ifp.close()
    ofp.close()
    return True


if __name__ == '__main__':
    in_f = ""
    out_f = ""
    alt = 0.0
    if len(sys.argv) >= 3:
        in_f = sys.argv[1]
        out_f = sys.argv[2]
        if len(sys.argv) >= 4:
            alt = float(sys.argv[3])
    else:
        sys.exit("usage: %s  infile.svx  outfile.svx  [altVal]" % sys.argv[0])

    if not svxNanChk(in_f, out_f, alt):
        sys.exit('%s failed.' % sys.argv[0])
