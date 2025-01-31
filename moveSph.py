#! /usr/bin/env python
#
# moveSph
#
import sys
import struct

def moveSphOrg(in_f, out_f, trv):
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

    # type record
    buff = struct.unpack('iiii', ifp.read(16))
    svType = buff[1]
    dType = buff[2]
    ofp.write(struct.pack('iiii', *buff))

    # size record
    if ( dType == 1 ):
        ofp.write(ifp.read(20))
    elif ( dType == 2 ):
        ofp.write(ifp.read(32))

    # org record
    if ( dType == 1 ):
        buff = struct.unpack('ifffi', ifp.read(20))
    elif ( dType == 2 ):
        buff = struct.unpack('idddi', ifp.read(32))
    org = [buff[1], buff[2], buff[3]]
    print('org : ', org,)
    org[0] = org[0] + trv[0]
    org[1] = org[1] + trv[1]
    org[2] = org[2] + trv[2]
    print(' => ', org)
    if ( dType == 1 ):
        ofp.write(struct.pack('ifffi',
                              buff[0], org[0], org[1], org[2], buff[4]))
    elif ( dType == 2 ):
        ofp.write(struct.pack('idddi',
                              buff[0], org[0], org[1], org[2], buff[4]))

    # pitch record
    if ( dType == 1 ):
        ofp.write(ifp.read(20))
    elif ( dType == 2 ):
        ofp.write(ifp.read(32))

    # time record
    if ( dType == 1 ):
        ofp.write(ifp.read(16))
    elif ( dType == 2 ):
        ofp.write(ifp.read(24))

    # data
    buff = struct.unpack('i', ifp.read(4))
    sz = buff[0]
    ofp.write(struct.pack('i', buff[0]))
    ofp.write(ifp.read(sz))
    ofp.write(ifp.read(4))

    # done
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
        sys.exit("usage: %s  infile.sph  outfile.sph  x y z" % sys.argv[0])

    if not moveSphOrg(in_f, out_f, trv):
        sys.exit('failed.')
