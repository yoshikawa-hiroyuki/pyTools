#! /usr/bin/env python
#
# d4dOmote2sla
#
"""converts DRAG4D Omote data file to STL/Ascii files
"""
import sys
import struct
import numpy


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


def convSurfaceElem(de, ifp, ofp):
    """converts DRAG4D shape element to STL/Ascii facets
    """
    if ifp.closed or ofp.closed: return False
    if de.max[0] < 2 or de.max[1] < 2: return False
    msz = de.max[0] * de.max[1]
    vts = numpy.array(0, dtype=float)
    nml = numpy.array(0, dtype=float)
    vts.resize((msz, 3))
    nml.resize((msz, 3))

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
            nv = nml[j*de.max[0] + i] \
                 + nml[j*de.max[0] + i+1] + nml[(j+1)*de.max[0] + i+1]
            nv = nv / 3.0
            ofp.write('facet normal %f %f %f\n' % (nv[0],nv[1],nv[2]))
            ofp.write('outer loop\n')
            ofp.write('vertex %f %f %f\n' % \
                      (vts[j*de.max[0] + i, 0],
                       vts[j*de.max[0] + i, 1],
                       vts[j*de.max[0] + i, 2]))
            ofp.write('vertex %f %f %f\n' % \
                      (vts[j*de.max[0] + i+1, 0],
                       vts[j*de.max[0] + i+1, 1],
                       vts[j*de.max[0] + i+1, 2]))
            ofp.write('vertex %f %f %f\n' % \
                      (vts[(j+1)*de.max[0] + i+1, 0],
                       vts[(j+1)*de.max[0] + i+1, 1],
                       vts[(j+1)*de.max[0] + i+1, 2]))
            ofp.write('endloop\nendfacet\n')

            # upper tria
            # lower tria
            nv = nml[j*de.max[0] + i] \
                 + nml[(j+1)*de.max[0] + i] + nml[(j+1)*de.max[0] + i+1]
            nv = nv / 3.0
            ofp.write('facet normal %f %f %f\n' % (nv[0],nv[1],nv[2]))
            ofp.write('outer loop\n')
            ofp.write('vertex %f %f %f\n' % \
                      (vts[j*de.max[0] + i, 0],
                       vts[j*de.max[0] + i, 1],
                       vts[j*de.max[0] + i, 2]))
            ofp.write('vertex %f %f %f\n' % \
                      (vts[(j+1)*de.max[0] + i+1, 0],
                       vts[(j+1)*de.max[0] + i+1, 1],
                       vts[(j+1)*de.max[0] + i+1, 2]))
            ofp.write('vertex %f %f %f\n' % \
                      (vts[(j+1)*de.max[0] + i, 0],
                       vts[(j+1)*de.max[0] + i, 1],
                       vts[(j+1)*de.max[0] + i, 2]))
            ofp.write('endloop\nendfacet\n')

    return True


def convert(srcf, dstf):
    """converts DRAG4D Omote data file to STL/Ascii files
    """
    # open srcfile
    try:
        ifp = open(srcf, "rb")
    except:
        print "open failed: %s" % srcf
        return -1

    # open dstfile
    try:
        ofp = open(dstf, "w")
    except:
        ifp.close()
        print "open failed: %s" % dstf
        return -1
    ofp.write('solid d4d_shape\n')

    de = D4dElem()
    while True:
        ret = de.Read(ifp)
        if ret != 1: break
        if de.flag != 1 and de.flag != 2 and de.flag != 3: # not supported
            if not de.Skip(ifp): break
            continue
        print 'converting %s(flag=%d)' % (de.gname, de.flag)
        if de.flag == 1:
            ifp.seek(12, 1) # skip
            continue
        if de.flag == 2:
            ifp.seek(de.max[0]*12, 1)
            ifp.seek(de.max[0]*20, 1)
            continue
        # de.flag == 3 : mesh
        ret = convSurfaceElem(de, ifp, ofp)
        if not ret:
            print 'element %s convert failed' % de.gname

    ofp.write('endsolid d4d_shape\n')
    ofp.close()
    ifp.close()
    return 0


if __name__ == '__main__':
    srcf = ""
    dstf = ""
    if ( len(sys.argv) > 2 ):
        srcf = sys.argv[1]
        dstf = sys.argv[2]
    else:
        sys.exit("usage: %s srcfile dstfile.sla" % sys.argv[0])

    ret = convert(srcf, dstf)
