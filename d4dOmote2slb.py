#! /usr/bin/env python
#
# d4dOmote2slb
#
"""converts DRAG4D Omote data file to STL/Binary files
"""
import sys
import struct
import numpy
defCmap = [[0.1, 0.1, 0.1], # 0 - black
           [0.8, 0.1, 0.1], # 1 - red
           [0.5, 0.8, 0.1], # 2 - light-green
           [0.9, 0.9, 0.1], # 3 - yellow
           [0.1, 0.1, 0.8], # 4 - blue
           [0.3, 0.5, 0.6], # 5 - magenta
           [0.1, 0.6, 0.6], # 6 - cyan
           [0.9, 0.9, 0.9]] # 7 - white


class D4dElem(object):
    """represents DRAG4D shape element
    """
    def __init__(self):
        self.flag = 0
        self.stp = 0
        self.etp = 0
        self.color = 7
        self.max = (0,0,0)
        self.gname = ''
        self.bo = '@'
        if sys.byteorder == 'little':
            self.bo = '>'  # DRAG4D data may be big-endian

    def iSize(self):
        """returns size of element data
        """
        return (self.etp - self.stp)*4

    def Read(self, fp):
        """reads basic parameters of element
        """
        if fp.closed: return -1
        buff = struct.unpack(self.bo+'i', fp.read(4)); self.flag = buff[0]
        if self.flag == 0:
            fp.seek(36, 1)
            return 0
        self.max = struct.unpack(self.bo+'3i', fp.read(12))
        buff = struct.unpack(self.bo+'i', fp.read(4)); self.stp = buff[0]
        buff = struct.unpack(self.bo+'i', fp.read(4)); self.etp = buff[0]
        self.gname = fp.read(8)
        buff = struct.unpack(self.bo+'i', fp.read(4)); self.color = buff[0]
        fp.read(4) # skip 4bytes
        return 1

    def Skip(self, fp):
        """skips element data
        """
        if fp.closed: return False
        if self.iSize() < 1: return False
        fp.seek(self.iSize(), 1)
        return True


def convSurfaceElem(de, ifp, dlst):
    """converts DRAG4D shape element to STL/Binary facets
    """
    if ifp.closed: return False
    if de.max[0] < 2 or de.max[1] < 2: return False
    msz = de.max[0] * de.max[1]
    vts = numpy.array(0, dtype=float)
    nml = numpy.array(0, dtype=float)
    vts.resize((msz, 3))
    nml.resize((msz, 3))

    # color
    cidx = de.color % len(defCmap)
    cval = (1 << 15) + (int(defCmap[cidx][0]*31.0) << 10) \
           + (int(defCmap[cidx][1]*31.0) << 5) + int(defCmap[cidx][2]*31.0)

    # read coordinates
    for i in range(0, msz):
        buff = struct.unpack(de.bo+'3i', ifp.read(12))
        vts[i,0] = buff[0] * 1e-6
        vts[i,1] = buff[1] * 1e-6
        vts[i,2] = buff[2] * 1e-6

    # skip id
    ifp.seek(msz * 4, 1)

    # read normals
    for i in range(0, msz):
        buff = struct.unpack(de.bo+'3i', ifp.read(12))
        nml[i,0] = buff[0] * 1e-6
        nml[i,1] = buff[1] * 1e-6
        nml[i,2] = buff[2] * 1e-6

    # skip utv, vtv
    ifp.seek(msz * 40, 1)

    # output
    for j in range(0, de.max[1]-1):
        for i in range(0, de.max[0]-1):
            # lower tria
            d1 = numpy.array(0, dtype=float); d1.resize(12)
            nv = nml[j*de.max[0] + i] \
                 + nml[j*de.max[0] + i+1] + nml[(j+1)*de.max[0] + i+1]
            nv = nv / 3.0
            d1[0:3] = nv[0:3]
            d1[3] = vts[j*de.max[0] + i, 0]
            d1[4] = vts[j*de.max[0] + i, 1]
            d1[5] = vts[j*de.max[0] + i, 2]
            d1[6] = vts[j*de.max[0] + i+1, 0]
            d1[7] = vts[j*de.max[0] + i+1, 1]
            d1[8] = vts[j*de.max[0] + i+1, 2]
            d1[9] = vts[(j+1)*de.max[0] + i+1, 0]
            d1[10] = vts[(j+1)*de.max[0] + i+1, 1]
            d1[11] = vts[(j+1)*de.max[0] + i+1, 2]
            D1 = (d1, cval)
            dlst.append(D1)

            # upper tria
            d2 = numpy.array(0, dtype=float); d2.resize(12)
            nv = nml[j*de.max[0] + i] \
                 + nml[(j+1)*de.max[0] + i] + nml[(j+1)*de.max[0] + i+1]
            nv = nv / 3.0
            d2[0:3] = nv[0:3]
            d2[3] = vts[j*de.max[0] + i, 0]
            d2[4] = vts[j*de.max[0] + i, 1]
            d2[5] = vts[j*de.max[0] + i, 2]
            d2[6] = vts[(j+1)*de.max[0] + i+1, 0]
            d2[7] = vts[(j+1)*de.max[0] + i+1, 1]
            d2[8] = vts[(j+1)*de.max[0] + i+1, 2]
            d2[9] = vts[(j+1)*de.max[0] + i, 0]
            d2[10] = vts[(j+1)*de.max[0] + i, 1]
            d2[11] = vts[(j+1)*de.max[0] + i, 2]
            D2 = (d2, cval)
            dlst.append(D2)

    return True


def convert(srcf, dstf):
    """converts DRAG4D Omote data file to STL/Binary files
    """
    # open srcfile
    try:
        ifp = open(srcf, "rb")
    except:
        print("open failed: %s" % srcf)
        return -1

    # conversion
    dlst = []
    de = D4dElem()
    while True:
        ret = de.Read(ifp)
        if ret != 1: break
        if de.flag != 1 and de.flag != 2 and de.flag != 3: # not supported
            if not de.Skip(ifp): break
            continue
        print('converting %s(flag=%d)' % (de.gname, de.flag))
        if de.flag == 1:
            ifp.seek(12, 1) # skip
            continue
        if de.flag == 2:
            ifp.seek(de.max[0]*12, 1)
            ifp.seek(de.max[0]*20, 1)
            continue
        # de.flag == 3 : mesh
        ret = convSurfaceElem(de, ifp, dlst)
        if not ret:
            print('element %s convert failed' % de.gname)

    ifp.close()
    if len(dlst) < 1:
        print("no valid shapes")
        return -1

    # open dstfile
    try:
        ofp = open(dstf, "w")
    except:
        ifp.close()
        print("open failed: %s" % dstf)
        return -1

    # write shapes
    print('writing into file(%d trias) ...' % len(dlst),)
    sys.stdout.flush()
    ofp.write(struct.pack('80s', 'converted d4d_shape'))
    ofp.write(struct.pack('i', len(dlst)))
    for i in range(len(dlst)):
        for j in range(12):
            ofp.write(struct.pack('f', dlst[i][0][j]))
        ofp.write(struct.pack('H', dlst[i][1]))
    ofp.close()
    print('done')
    return 0


if __name__ == '__main__':
    srcf = ""
    dstf = ""
    if ( len(sys.argv) > 2 ):
        srcf = sys.argv[1]
        dstf = sys.argv[2]
    else:
        sys.exit("usage: %s srcfile dstfile.slb" % sys.argv[0])

    ret = convert(srcf, dstf)
