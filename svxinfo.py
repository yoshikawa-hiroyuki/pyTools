#! /usr/bin/env python
#
# svxinfo
#
"""report SVX file information
"""
import sys
import struct


def scanSvx(tgtf):
    """ scan SVX file and report to stdout
    
        ARGS
          tgtf : path of SVX file to scan

        RETURNS
          0 : succeed
          -1 : failed
    """
    # open file
    try:
        ifp = open(tgtf, "rb")
    except:
        print("open failed: %s" % tgtf)
        return -1

    # size record
    buff = struct.unpack('5i', ifp.read(20))
    dims = (buff[1], buff[2], buff[3])
    print("dims = ", dims)
    if buff[0] != 12 or buff[4] != 12:
        print("* warning: sz field of SIZE record is invalid *")

    # org record
    buff = struct.unpack('i3fi', ifp.read(20))
    org = (buff[1], buff[2], buff[3])
    print("org = ", org)
    if buff[0] != 12 or buff[4] != 12:
        print("* warning: sz field of ORIG record is invalid *")

    # pitch record
    buff = struct.unpack('i3fi', ifp.read(20))
    pitch = (buff[1], buff[2], buff[3])
    print("pitch = ", pitch)
    if buff[0] != 12 or buff[4] != 12:
        print("* warning: sz field of PITCH record is invalid *")

    # type record
    buff = struct.unpack('iii', ifp.read(12))
    dtype = buff[1]
    dtMap = {"VolRate":False, "OpenRate":False,
             "Medium":False, "VoxBC":False, "FaceBC":False}
    print("type = ", dtype, "(",)
    if ( dtype == 0 ):
        dtype = 31
    if ( dtype & 1 ):
        dtMap["VolRate"] = True
        print("VolRate",)
    if ( dtype & 2 ):
        dtMap["OpenRate"] = True
        print("OpenRate",)
    if ( dtype & 4 ):
        dtMap["Medium"] = True
        print("Medium",)
    if ( dtype & 8 ):
        dtMap["VoxBC"] = True
        print("VoxBC",)
    if ( dtype & 16 ):
        dtMap["FaceBC"] = True
        print("FaceBC",)
    print(")")
    if buff[0] != 4 or buff[2] != 4:
        print("* warning: sz field of TYPE record is invalid *")

    # VolRate record
    if ( dtMap["VolRate"] ):
        print("scanning VolRate record ...",)
        sys.stdout.flush()
        buff = struct.unpack('i', ifp.read(4))
        dimSz = dims[0] * dims[1] * dims[2]
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of VolRate DATA record is invalid *")

        # read the first data
        nanFound = False
        vals = struct.unpack('f', ifp.read(4))
        minV = vals[0]
        maxV = vals[0]
        if vals[0] != vals[0]:
            nanFound = True
        # read datas folowing
        for i in xrange(1, dimSz):
            vals = struct.unpack('f', ifp.read(4))
            if ( minV > vals[0] ):
                minV = vals[0]
            elif ( maxV < vals[0] ):
                maxV = vals[0]
            if vals[0] != vals[0]:
                nanFound = True
        buff = struct.unpack('i', ifp.read(4))
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of VolRate DATA record is invalid *")

        print("\rVolRate min = ", minV, ", max = ", maxV)
        if nanFound:
            print("\rVolRate NaN found.")

    # OpenRate record
    if ( dtMap["OpenRate"] ):
        # X
        print("scanning OpenRate[X] record ...",)
        sys.stdout.flush()
        buff = struct.unpack('i', ifp.read(4))
        dimSz = (dims[0]+1) * dims[1] * dims[2]
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of OpenRate[X] DATA record is invalid *")

        # read the first data
        nanFound = False
        vals = struct.unpack('f', ifp.read(4))
        minV = vals[0]
        maxV = vals[0]
        if vals[0] != vals[0]:
            nanFound = True
        # read datas folowing
        for i in xrange(1, dimSz):
            vals = struct.unpack('f', ifp.read(4))
            if ( minV > vals[0] ):
                minV = vals[0]
            elif ( maxV < vals[0] ):
                maxV = vals[0]
            if vals[0] != vals[0]:
                nanFound = True
        buff = struct.unpack('i',  ifp.read(4))
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of OpenRate[X] DATA record is invalid *")
        print("\rOpenRate[X] min = ", minV, ", max = ", maxV)
        if nanFound:
            print("\rOpenRate[X] NaN found.")

        # Y
        print("scanning OpenRate[Y] record ...",)
        sys.stdout.flush()
        buff = struct.unpack('i', ifp.read(4))
        dimSz = dims[0] * (dims[1]+1) * dims[2]
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of OpenRate[Y] DATA record is invalid *")

        # read the first data
        nanFound = False
        vals = struct.unpack('f', ifp.read(4))
        minV = vals[0]
        maxV = vals[0]
        if vals[0] != vals[0]:
            nanFound = True
        # read datas folowing
        for i in xrange(1, dimSz):
            vals = struct.unpack('f', ifp.read(4))
            if ( minV > vals[0] ):
                minV = vals[0]
            elif ( maxV < vals[0] ):
                maxV = vals[0]
            if vals[0] != vals[0]:
                nanFound = True
        buff = struct.unpack('i', ifp.read(4))
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of OpenRate[Y] DATA record is invalid *")

        print("\rOpenRate[Y] min = ", minV, ", max = ", maxV)
        if nanFound:
            print("\rOpenRate[Y] NaN found.")
    
        # Z
        print("scanning OpenRate[Z] record ...",)
        sys.stdout.flush()
        buff = struct.unpack('i', ifp.read(4))
        dimSz = dims[0] * dims[1] * (dims[2]+1)
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of OpenRate[Z] DATA record is invalid *")

        # read the first data
        nanFound = False
        vals = struct.unpack('f', ifp.read(4))
        minV = vals[0]
        maxV = vals[0]
        if vals[0] != vals[0]:
            nanFound = True
        # read datas folowing
        for i in xrange(1, dimSz):
            vals = struct.unpack('f', ifp.read(4))
            if ( minV > vals[0] ):
                minV = vals[0]
            elif ( maxV < vals[0] ):
                maxV = vals[0]
            if vals[0] != vals[0]:
                nanFound = True
        buff = struct.unpack('i', ifp.read(4))
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of OpenRate[Z] DATA record is invalid *")

        print("\rOpenRate[Z] min = ", minV, ", max = ", maxV)
        if nanFound:
            print("\rOpenRate[Z] NaN found.")

    # Medium record
    if ( dtMap["Medium"] ):
        print("scanning Medium record ...",)
        sys.stdout.flush()
        buff = struct.unpack('i', ifp.read(4))
        dimSz = dims[0] * dims[1] * dims[2]
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of VoxMedium DATA record is invalid *")

        # read the first data
        nanFound = False
        idLst = {}
        vals = struct.unpack('i', ifp.read(4))
        idLst[vals[0]] = 1
        if vals[0] != vals[0]:
            nanFound = True
        # read datas folowing
        for i in xrange(1, dimSz):
            vals = struct.unpack('i', ifp.read(4))
            try:
                idLst[vals[0]] = idLst[vals[0]] + 1
            except KeyError:
                idLst[vals[0]] = 1
            if vals[0] != vals[0]:
                nanFound = True
        buff = struct.unpack('i', ifp.read(4))
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of VoxMedium DATA record is invalid *")

        print("\rMedium = ", idLst.keys(),)
        if ( len(idLst) < 5 ):
            print("                   ")
        else:
            print("")
        if nanFound:
            print("\rMedium NaN found.")

    # VoxBC record
    if ( dtMap["VoxBC"] ):
        print("scanning VoxBC record ...",)
        sys.stdout.flush()
        buff = struct.unpack('i', ifp.read(4))
        dimSz = dims[0] * dims[1] * dims[2]
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of VoxBC DATA record is invalid *")

        # read the first data
        nanFound = False
        idLst = {}
        vals = struct.unpack('i', ifp.read(4))
        idLst[vals[0]] = 1
        if vals[0] != vals[0]:
            nanFound = True
        # read datas folowing
        for i in xrange(1, dimSz):
            vals = struct.unpack('i', ifp.read(4))
            try:
                idLst[vals[0]] = idLst[vals[0]] + 1
            except KeyError:
                idLst[vals[0]] = 1
            if vals[0] != vals[0]:
                nanFound = True
        buff = struct.unpack('i', ifp.read(4))
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of VoxBC DATA record is invalid *")

        print("\rVoxBC = ", idLst.keys(),)
        if ( len(idLst) < 5 ):
            print("                   ")
        else:
            print("")
        if nanFound:
            print("\rVoxBC NaN found.")

    # FaceBC record
    if ( dtMap["FaceBC"] ):
        # X
        print("scanning FaceBC[X] record ...",)
        sys.stdout.flush()
        buff = struct.unpack('i', ifp.read(4))
        dimSz = (dims[0]+1) * dims[1] * dims[2]
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of FaceBC[X] DATA record is invalid *")

        # read the first data
        nanFound = False
        vals = struct.unpack('i', ifp.read(4))
        idLst = {}
        idLst[vals[0]] = 1
        if vals[0] != vals[0]:
            nanFound = True
        # read datas folowing
        for i in xrange(1, dimSz):
            vals = struct.unpack('i', ifp.read(4))
            try:
                idLst[vals[0]] = idLst[vals[0]] + 1
            except KeyError:
                idLst[vals[0]] = 1
            if vals[0] != vals[0]:
                nanFound = True
        buff = struct.unpack('i', ifp.read(4))
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of FaceBC[X] DATA record is invalid *")

        print("\rFaceBC[X] = ", idLst.keys(),)
        if ( len(idLst) < 5 ):
            print("                   ")
        else:
            print("")
        if nanFound:
            print("\rFaceBC[X] NaN found.")

        # Y
        print("scanning FaceBC[Y] record ...",)
        sys.stdout.flush()
        buff = struct.unpack('i', ifp.read(4))
        dimSz = dims[0] * (dims[1]+1) * dims[2]
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of FaceBC[Y] DATA record is invalid *")

        # read the first data
        nanFound = False
        vals = struct.unpack('i', ifp.read(4))
        idLst = {}
        idLst[vals[0]] = 1
        if vals[0] != vals[0]:
            nanFound = True
        # read datas folowing
        for i in xrange(1, dimSz):
            vals = struct.unpack('i', ifp.read(4))
            try:
                idLst[vals[0]] = idLst[vals[0]] + 1
            except KeyError:
                idLst[vals[0]] = 1
            if vals[0] != vals[0]:
                nanFound = True
        buff = struct.unpack('i', ifp.read(4))
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of FaceBC[Y] DATA record is invalid *")

        print("\rFaceBC[Y] = ", idLst.keys(),)
        if ( len(idLst) < 5 ):
            print("                   ")
        else:
            print("")
        if nanFound:
            print("\rFaceBC[Y] NaN found.")

        # Z
        print("scanning FaceBC[Z] record ...",)
        sys.stdout.flush()
        buff = struct.unpack('i', ifp.read(4))
        dimSz = dims[0] * dims[1] * (dims[2]+1)
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of FaceBC[Z] DATA record is invalid *")

        # read the first data
        nanFound = False
        vals = struct.unpack('i', ifp.read(4))
        idLst = {}
        idLst[vals[0]] = 1
        if vals[0] != vals[0]:
            nanFound = True
        # read datas folowing
        for i in xrange(1, dimSz):
            vals = struct.unpack('i', ifp.read(4))
            try:
                idLst[vals[0]] = idLst[vals[0]] + 1
            except KeyError:
                idLst[vals[0]] = 1
            if vals[0] != vals[0]:
                nanFound = True
        buff = struct.unpack('i', ifp.read(4))
        if buff[0] != 4 * dimSz:
            print("* warning: sz field of FaceBC[Z] DATA record is invalid *")

        print("\rFaceBC[Z] = ", idLst.keys(),)
        if ( len(idLst) < 5 ):
            print("                   ")
        else:
            print("")
        if nanFound:
            print("\rFaceBC[Z] NaN found.")

    ifp.close()
    return 0


if __name__ == '__main__':
    tgtf = ""
    if ( len(sys.argv) > 1 ):
        tgtf = sys.argv[1]
    else:
        sys.exit("usage: %s targetfile.svx" % sys.argv[0])
    scanSvx(tgtf)
