#! /usr/bin/env python
#
# fdvolinfo
#
"""report 4DVis Volume data file information
"""
import sys
import struct


def scanFDVol(tgtf):
    """ scan 4DVis Volume data file and report to stdout

        ARGS
          tgtf : path of .vol file to scan

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
  
    # type record
    bo = '<'
    header = ifp.read(20)
    buff = struct.unpack(bo+'iiiii', header)
    if buff[0] == 12:
        dims = (buff[1], buff[2], buff[3])
    else:
        bo = '>'
        buff = struct.unpack(bo+'iiiii', header)
        if buff[0] == 12:
            dims = (buff[1], buff[2], buff[3])
        else:
            ifp.close()
            print "invalid file, not 4DVis volume?"
            return -1

    if bo == '<':
        print 'endian = little'
    else:
        print 'endian = big'
    print "dims = ", dims
    
    # time record
    buff = struct.unpack(bo+'iifi', ifp.read(16))
    step = buff[1]
    tm = buff[2]
    print "time step = ", step, " (", tm, ")"
    
    # bbox record
    buff = struct.unpack(bo+'iffffffi', ifp.read(32))
    org = (buff[1], buff[2], buff[3])
    gro = (buff[4], buff[5], buff[6])
    print "bbox min = ", org
    print "bbox max = ", gro

    # data sz
    dataSz = dims[0] * dims[1] * dims[2]
    if (dataSz % 4) != 0:
        dataSz = dims[0] * dims[1] * dims[2] + 4 \
            - (dims[0] * dims[1] * dims[2] % 4)
    recordSz = dataSz + 8
    print "record size = ", recordSz

    print "scanning data record ",
    sys.stdout.flush()

    # step loop
    stp = 0
    while True:
        try:
            if len(ifp.read(recordSz)) < 1:
                break # eof
            print ".",
            sys.stdout.flush()
        except:
            break # eof
        stp = stp + 1
        continue
    print " done."
    print "#of step = ", stp

    ifp.close()
    return 0


if __name__ == '__main__':
    tgtf = ""
    if ( len(sys.argv) > 1 ):
        tgtf = sys.argv[1]
    else:
        sys.exit("usage: %s targetfile.vol" % sys.argv[0])

    ret = scanFDVol(tgtf)
    sys.exit(ret)
