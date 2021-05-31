#! /usr/bin/env python
#
# xformObj
#  transform Wavefront OBJ file
#
import sys, math
try:
    import numpy as N
except:
    sys.exit('%s: can not import numpy, quit.' % sys.argv[0])
_dt = N.dtype('f4')

class Mat4(object):
    def __init__(self, org =None):
        if org and isinstance(org, Mat4):
            self.m_v = N.array([x for x in org.m_v], _dt)
        else:
            try:
                self.m_v = N.array([x for x in org], _dt)
            except:
                self.m_v = N.array([0.0 for i in range(16)], _dt)
                self.Identity()
    def Identity(self):
        self.m_v[0:] = 0.0
        self.m_v[0] = self.m_v[5] = self.m_v[10] = self.m_v[15] = 1.0
    def __mul__(self, m):
        if isinstance(m, Mat4):
            w = Mat4()
            for i in range(4):
                for j in range(4):
                    w.m_v[i*4 +j] = 0.0
                    for k in range(4):
                        l = i * 4
                        w.m_v[l + j] += (self.m_v[j + k*4] * m.m_v[l + k])
            return w
        try:
            w = [0.0, 0.0, 0.0]
            for i in range(0,3):
                for k in range(0,3):
                    w[i] += (self.m_v[i + k*4] * m[k])
                w[i] += self.m_v[i + 12]
            return w
        except:
            w = Mat4([x*m for x in self.m_v])
            return w
    def Scale(self, s):
        w = Mat4()
        try:
            w.m_v[0] = s[0]; w.m_v[5] = s[1]; w.m_v[10] = s[2]
        except:
            w.m_v[0] = w.m_v[5] = w.m_v[10] = s
        x = self * w
        self.m_v[0:] = x.m_v[0:]
    def Translate(self, t):
        w = Mat4()
        try:
            w.m_v[12] = t[0]; w.m_v[13] = t[1]; w.m_v[14] = t[2]
        except:
            w.m_v[12] = w.m_v[13] = w.m_v[14] = t
        x = self * w
        self.m_v[0:] = x.m_v[0:]
    def RotX(self, rx):
        w = Mat4()
        w.m_v[ 5] = math.cos(rx)
        w.m_v[ 6] = math.sin(rx)
        w.m_v[ 9] =-w.m_v[ 6]
        w.m_v[10] = w.m_v[ 5]
        x = self * w
        self.m_v[0:] = x.m_v[0:]
    def RotY(self, ry):
        w = Mat4()
        w.m_v[ 0] = math.cos(ry)
        w.m_v[ 8] = math.sin(ry)
        w.m_v[ 2] =-w.m_v[ 8]
        w.m_v[10] = w.m_v[ 0]
        x = self * w
        self.m_v[0:] = x.m_v[0:]
    def RotZ(self, rz):
        w = Mat4()
        w.m_v[ 0] = math.cos(rz)
        w.m_v[ 1] = math.sin(rz)
        w.m_v[ 4] =-w.m_v[ 1]
        w.m_v[ 5] = w.m_v[ 0]
        x = self * w
        self.m_v[0:] = x.m_v[0:]

def Deg2Rad(x):
    return (x * math.pi / 180.0)


def xformObj(in_f, out_f,
             Tv=[0.0,0.0,0.0], Sv=[1.0,1.0,1.0], Rv=[0.0,0.0,0.0]):
    # open input file
    try:
        ifp = open(in_f, "r")
    except:
        print("open failed: %s" % in_f)
        return False

    # open output file
    try:
        ofp = open(out_f, "w")
    except:
        print("open failed: %s" % out_f)
        ifp.close()
        return False

    # matrix for v
    m = Mat4()
    m.Translate(Tv)
    m.RotY(Deg2Rad(Rv[1]))
    m.RotX(Deg2Rad(Rv[0]))
    m.RotZ(Deg2Rad(Rv[2]))
    m.Scale(Sv)

    # matrix for vn
    m2 = Mat4()
    m2.RotY(Deg2Rad(Rv[1]))
    m2.RotX(Deg2Rad(Rv[0]))
    m2.RotZ(Deg2Rad(Rv[2]))

    # main loop
    for line in ifp:
        itemList = line.strip().split()
        if len(itemList) > 3 and itemList[0] == 'v':
            v = [float(itemList[1]), float(itemList[2]), float(itemList[3])]
            v1 = m * v
            ofp.write('v %f %f %f\n' % (v1[0], v1[1], v1[2]))
        elif len(itemList) > 3 and itemList[0] == 'vn':
            v = [float(itemList[1]), float(itemList[2]), float(itemList[3])]
            v1 = m2 * v
            ofp.write('vn %f %f %f\n' % (v1[0], v1[1], v1[2]))
        else:
            ofp.write(line)

    # done
    ifp.close()
    ofp.close()
    return True

def usage(prog):
    sys.exit("usage: %s [-h][-t tx ty tz][-s sx sy sz][-r rx ry rz] \\\n"
             "         infile.obj outfile.obj" % prog)

if __name__ == '__main__':
    in_f = ""
    out_f = ""
    Tv = [0.0, 0.0, 0.0]
    Sv = [1.0, 1.0, 1.0]
    Rv = [0.0, 0.0, 0.0]

    # parse args
    argIdx = 1
    argc = len(sys.argv)
    if argc < 2:
        usage(sys.argv[0])

    while argIdx < argc:
        if sys.argv[argIdx] == '-h':
            usage(sys.argv[0])
        elif sys.argv[argIdx] == '-t':
            if argIdx+5 < argc:
                Tv[0] = float(sys.argv[argIdx+1])
                Tv[1] = float(sys.argv[argIdx+2])
                Tv[2] = float(sys.argv[argIdx+3])
                argIdx = argIdx + 4
                continue
            else:
                usage(sys.argv[0])
        elif sys.argv[argIdx] == '-s':
            if argIdx+5 < argc:
                Sv[0] = float(sys.argv[argIdx+1])
                Sv[1] = float(sys.argv[argIdx+2])
                Sv[2] = float(sys.argv[argIdx+3])
                argIdx = argIdx + 4
                continue
            else:
                usage(sys.argv[0])
        elif sys.argv[argIdx] == '-r':
            if argIdx+5 < argc:
                Rv[0] = float(sys.argv[argIdx+1])
                Rv[1] = float(sys.argv[argIdx+2])
                Rv[2] = float(sys.argv[argIdx+3])
                argIdx = argIdx + 4
                continue
            else:
                usage(sys.argv[0])
        else:
            break

    in_f = sys.argv[argIdx]
    out_f = sys.argv[argIdx+1]

    # do conversion
    if not xformObj(in_f, out_f, Tv, Sv, Rv):
        sys.exit('conversion failed.')

    sys.exit(0)
