#! /usr/bin/env python
#
# sphinfo
#
"""report SPH file information
"""
import sys
import struct


def scanSph(tgtf):
    """ scan SPH file and report to stdout

        ARGS
          tgtf : path of SPH file to scan

        RETURNS
          0 : succeed
          -1 : failed
    """
    # open file
    try:
        ifp = open(tgtf, 'rb')
    except:
        print 'open failed: %s' % tgtf
        return -1
  
    # type record
    bo = '<'
    header = ifp.read(16)
    buff = struct.unpack(bo+'iiii', header)
    svType = buff[1]
    dType = buff[2]
    print 'svType = ', svType,
    if ( svType == 1 ):
        print '(scalar)'
    elif ( svType == 2 ):
        print '(vector)'
    else:
        bo = '>'
        buff = struct.unpack(bo+'iiii', header)
        svType = buff[1]
        dType = buff[2]
        print 'svType = ', svType,
        if ( svType == 1 ):
            print '(scalar)'
        elif ( svType == 2 ):
            print '(vector)'
        else:
            ifp.close()
            print 'invalid svType: %s' % dType
            return -1

    if bo == '<':
        print 'endian = little'
    else:
        print 'endian = big'

    print 'dType = ', dType,
    if ( dType == 1 ):
        print '(single precision)'
    elif ( dType == 2 ):
        print '(double precision)'
    else:
        ifp.close()
        print 'invalid dType: %s' % dType
        return -1
    
    # size record
    if ( dType == 1 ):
        buff = struct.unpack(bo+'iiiii', ifp.read(20))
        dims = (buff[1], buff[2], buff[3])
    elif ( dType == 2 ):
        buff = struct.unpack(bo+'i', ifp.read(4))
        buff = struct.unpack(bo+'qqq', ifp.read(24))
        dims = (buff[0], buff[1], buff[2])
        buff = struct.unpack(bo+'i', ifp.read(4))
    
    print 'dims = ', dims
    
    # org record
    if ( dType == 1 ):
        buff = struct.unpack(bo+'ifffi', ifp.read(20))
        org = (buff[1], buff[2], buff[3])
    elif ( dType == 2 ):
        buff = struct.unpack(bo+'i', ifp.read(4))
        buff = struct.unpack(bo+'ddd', ifp.read(24))
        org = (buff[0], buff[1], buff[2])
        buff = struct.unpack(bo+'i', ifp.read(4))
    
    print 'org = ', org
    
    # pitch record
    if ( dType == 1 ):
        buff = struct.unpack(bo+'ifffi', ifp.read(20))
        pitch = (buff[1], buff[2], buff[3])
    elif ( dType == 2 ):
        buff = struct.unpack(bo+'i', ifp.read(4))
        buff = struct.unpack(bo+'ddd', ifp.read(24))
        pitch = (buff[0], buff[1], buff[2])
        buff = struct.unpack(bo+'i', ifp.read(4))
    
    print 'pitch = ', pitch
    
    # time record
    if ( dType == 1 ):
        buff = struct.unpack(bo+'iifi', ifp.read(16))
        step = buff[1]
        tm = buff[2]
    elif ( dType == 2 ):
        buff = struct.unpack(bo+'i', ifp.read(4))
        buff = struct.unpack(bo+'qd', ifp.read(16))
        step = buff[0]
        tm = buff[1]
        buff = struct.unpack(bo+'i', ifp.read(4))
    
    print 'time step = ', step, ' (', tm, ')'
    
    # skip data sz
    print 'scanning data record ...\r',
    sys.stdout.flush()
    ifp.read(4)
    
    dimSz = dims[0] * dims[1] * dims[2]
    vlen = 0
    if ( svType == 1 ):
        vlen = 1
        if ( dType == 1 ):
            packStr = 'f'
            dlen = 4
        else:
            packStr = 'd'
            dlen = 8
    else:
        vlen = 3
        if ( dType == 1 ):
            packStr = 'fff'
            dlen = 12
        else:
            packStr = 'ddd'
            dlen = 24
    
    # read the first data
    nanFound = False
    vals = struct.unpack(bo+packStr, ifp.read(dlen))
    minV = {}
    maxV = {}
    for l in range(0, vlen):
        if vals[l] != vals[l]:
            nanFound = True
        minV[l] = vals[l]
        maxV[l] = vals[l]
    
    # read datas folowing
    for i in range(1, dimSz):
        vals = struct.unpack(bo+packStr, ifp.read(dlen))
        for l in range(0, vlen):
            if not nanFound and vals[l] != vals[l]:
                nanFound = True
            if ( minV[l] > vals[l] ):
                minV[l] = vals[l]
            elif ( maxV[l] < vals[l] ):
                maxV[l] = vals[l]
    
    # skip data sz
    #ifp.read(4)
    ifp.close()

    for l in range(0, vlen):
        print 'data[', l, '] min = ', minV[l], ', max = ', maxV[l]
    if nanFound:
        print 'NaN found.'
    return 0


if __name__ == '__main__':
    tgtf = ''
    if ( len(sys.argv) > 1 ):
        tgtf = sys.argv[1]
    else:
        sys.exit('usage: %s targetfile.sph' % sys.argv[0])

    ret = scanSph(tgtf)
    sys.exit(ret)
