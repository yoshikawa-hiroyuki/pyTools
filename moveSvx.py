#! /usr/bin/env python
#
# moveSvx
#
import sys
import struct

def moveSvxOrg(in_f, out_f, trv):
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
    ofp.write(ifp.read(20))

    # org record
    buff = struct.unpack('i3fi', ifp.read(20))
    org = [buff[1], buff[2], buff[3]]
    print('org : ', org,)
    org[0] = org[0] + trv[0]
    org[1] = org[1] + trv[1]
    org[2] = org[2] + trv[2]
    print(' => ', org)
    ofp.write(struct.pack('i3fi', buff[0], org[0], org[1], org[2], buff[4]))

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

    ifp.close()
    ofp.close()
    return True


if __name__ == '__main__':
    in_f = ""
    out_f = ""
    trv = [0.0, 0.0, 0.0]
    if len(sys.argv) >= 6:
        in_f = sys.argv[1]
        out_f = sys.argv[2]
        trv[0] = float(sys.argv[3])
        trv[1] = float(sys.argv[4])
        trv[2] = float(sys.argv[5])
    else:
        sys.exit("usage: %s  infile.svx  outfile.svx  x y z" % sys.argv[0])

    if not moveSvxOrg(in_f, out_f, trv):
        sys.exit('replace failed.')
