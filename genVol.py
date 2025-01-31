#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
NAME
  genVol

DESCRIPTION
  画像データファイル群から、ボリュームデータ生成を生成します。

USAGE
  python genVol.py -o outfile [-bb x0 y0 z0 x1 y1 z1] infile1 infile2 ...

  -o outfile
    生成するボリュームデータファイルのパスを指定します。省略はできません。
    指定するファイルのフォーマットは、ファイル名の拡張子で判断されます。
    .vol .fdv : 4D Visualizerボリュームデータファイル
    .dat .avs : AVSボリュームデータファイル
    .sph      : V-Sphere/Sphere SPHファイルフォーマット(スカラー)

  -bb x0 y0 z0 x1 y1 z1
    バウンディングボックスを指定します。
    バウンディングボックスは、ボリュームデータが存在する立方体領域の
    最小頂点座標(x0, y0, z0)および最大頂点座標座標(x1, y1, z1)です。
    省略した場合は、(x0, y0, z0) = (0, 0, 0)、
    (x1, y1, z1) = (IMAX-1, JMAX-1, KMAX-1)とみなされます。ここで、
    (IMAX, JMAX, KMAX)は、ボリュームデータのサイズです。

  infile1 infile2 ...
    入力する画像ファイル群を指定します。指定した画像ファイルの数が
    生成されるボリュームデータのKMAXになります。
    画像ファイルのフォーマットは、ファイル名の拡張子で判断されます。
    .png : PNG
    .ppm : Portable Pixmap
    .pgm : Portable Graymap
    .bmp : Microsoft Bitmap
    .jpg : JPEG/JFIF
    .gif : GIF
    .tif : TIFF
    .dcm : DICOM(非圧縮のみ)

DEPENDENCY
  以下に示すパッケージがPython環境にインストールされている必要があります。
  PIL - Python Imaging Library  http://www.pythonware.com/products/pil/
  pydicom (DICOMファイル入力時) http://code.google.com/p/pydicom/

"""
import sys, glob, operator
import struct
try:
    import Image
except:
    print('%s: import Image failed, PIL may not installed' % sys.argv[0])


def usage():
    print('usage: %s -o outfile [-bb x0 y0 z0 x1 y1 z1] infile1 infile2 ...' \
        % sys.argv[0])
    return

def LoadImage(filename):
    if len(filename) < 4:
        return None # unknown format
    if filename[-3:] == 'dcm':
        try:
            import dicom
        except:
            print('%s: import dicom failed, pydicom may not installed' \
                % sys.argv[0])
            return None
        try:
            dataset = dicom.read_file(filename)
        except:
            print('%s: can not read dicom file: %s' % (sys.argv[0], filename))
            return None
        bits = dataset.BitsAllocated
        samples = dataset.SamplesPerPixel
        if bits == 8 and samples == 1:
            mode = 'L'
        elif bits == 8 and samples == 3:
            mode = 'RGB'
        elif bits == 16:
            mode = 'I;16'
        else:
            print('%s: can not figure out PIL mode for %s' \
                % (sys.argv[0], filename))
            return None
        size = (dataset.Columns, dataset.Rows)
        im = Image.frombuffer(mode, size, dataset.PixelData, 'raw', mode, 0, 1)
        return im.convert('L')
    else:
        return Image.open(filename).convert('L')


def CreateFdvVol(outfile, infiles, bbox=None):
    dims = [0, 0, 0]
    img = LoadImage(infiles[0])
    if not img:
        print('%s: open failed: %s' % (sys.argv[0], infiles[0]))
        return -1
    (dims[0], dims[1]) = img.size
    if dims[0] * dims[1] < 1:
        print('%s: invalid input image: %s' % (sys.argv[0], infiles[0]))
        return -1
    dims[2] = len(infiles)

    try:
        ofp = open(outfile, 'wb')
    except:
        print('%s: open failed: %s' % (sys.argv[0], outfile))
        return -1

    # size
    ofp.write(struct.pack('5i', 12, dims[0], dims[1], dims[2], 12))

    # time
    ofp.write(struct.pack('iifi', 8, 0, 0.0, 8))

    # bbox
    if not bbox:
        ofp.write(struct.pack('iffffffi', 24, 0, 0, 0,
                              dims[0]-1, dims[1]-1, dims[2]-1, 24))
    else:
        ofp.write(struct.pack('iffffffi', 24,
                              bbox[0][0], bbox[0][1], bbox[0][2], bbox[1][0],
                              bbox[1][1], bbox[1][2], 24))
    # datas
    ofp.write(struct.pack('i', dims[0]*dims[1]*dims[2]))

    for z in range(dims[2]):
        print('  converting %s ...' % infiles[z],)
        img = LoadImage(infiles[z])
        if not img:
            print('%s: open failed: %s' % (sys.argv[0], infiles[z]))
            ofp.close()
            return -1
        if img.size[0] != dims[0] or img.size[1] != dims[1]:
            print('%s: image size not match: %s' % (sys.argv[0], infiles[z]))
            ofp.close()
            return -1
        ofp.write(img.tostring())
        print('done')
        continue

    ofp.write(struct.pack('i', dims[0]*dims[1]*dims[2]))
    ofp.close()
    return 0

def CreateAvsVol(outfile, infiles, bbox=None):
    dims = [0, 0, 0]
    img = LoadImage(infiles[0])
    if not img:
        print('%s: open failed: ' % (sys.argv[0], infiles[0]))
        return -1
    (dims[0], dims[1]) = img.size
    if dims[0] * dims[1] < 1:
        print('%s: invalid input image: %s' % (sys.argv[0], infiles[0]))
        return -1
    dims[2] = len(infiles)
    if dims[0] > 255 or dims[1] > 255 or dims[2] > 255:
        print('%s: invalid input image size' % sys.argv[0])
        return -1
    
    try:
        ofp = open(outfile, 'wb')
    except:
        print('%s: open failed: %s' % (sys.argv[0], outfile))
        return -1

    # size
    ofp.write(struct.pack('3B', dims[0], dims[1], dims[2]))

    # datas
    for z in range(dims[2]):
        print('  converting %s ...' % infiles[z],)
        img = LoadImage(infiles[z])
        if not img:
            print('%s: open failed: %s' % (sys.argv[0], infiles[z]))
            ofp.close()
            return -1
        if img.size[0] != dims[0] or img.size[1] != dims[1]:
            print('%s: image size not match: %s' % (sys.argv[0], infiles[z]))
            ofp.close()
            return -1
        ofp.write(img.tostring())
        print('done')
        continue

    ofp.close()
    return 0

def CreateSph(outfile, infiles, bbox=None):
    dims = [0, 0, 0]
    img = LoadImage(infiles[0])
    if not img:
        print('%s: open failed: %s' % (sys.argv[0], infiles[0]))
        return -1
    (dims[0], dims[1]) = img.size
    if dims[0] * dims[1] < 1:
        print('%s: invalid input image: %s' % (sys.argv[0], infiles[0]))
        return -1
    dims[2] = len(infiles)

    try:
        ofp = open(outfile, 'wb')
    except:
        print('%s: open failed: %s' % (sys.argv[0], outfile))
        return -1

    # header
    ofp.write(struct.pack('4i', 8, 1, 1, 8))

    # size
    ofp.write(struct.pack('5i', 12, dims[0], dims[1], dims[2], 12))

    # bbox
    if not bbox:
        ofp.write(struct.pack('ifffiifffi', 12, 0, 0, 0, 12, 12, 1, 1, 1, 12))
    else:
        pitch = [(bbox[1][0] - bbox[0][0]) / (dims[0] - 1),
                 (bbox[1][1] - bbox[0][1]) / (dims[1] - 1),
                 (bbox[1][2] - bbox[0][2]) / (dims[2] - 1)]
        ofp.write(struct.pack('ifffi', 12,
                              bbox[0][0], bbox[0][1], bbox[0][2], 12))
        ofp.write(struct.pack('ifffi', 12, pitch[0], pitch[1], pitch[2], 12))

    # time
    ofp.write(struct.pack('iifi', 8, 0, 0.0, 8))

    # datas
    ofp.write(struct.pack('i', dims[0] * dims[1] * dims[2] * 4))

    for z in range(dims[2]):
        print('  converting %s ...' % infiles[z],)
        img = LoadImage(infiles[z])
        if not img:
            print('%s: open failed: %s' % (sys.argv[0], infiles[z]))
            ofp.close()
            return -1
        if img.size[0] != dims[0] or img.size[1] != dims[1]:
            print('%s: image size not match: %s' % (sys.argv[0], infiles[z]))
            ofp.close()
            return -1
        for y in range(dims[1]):
            for x in range(dims[0]):
                val = float(img.getpixel((x, y)))
                ofp.write(struct.pack('f', val))
        print('done')
        continue

    ofp.write(struct.pack('i', dims[0]*dims[1]*dims[2]*4))
    ofp.close()


if __name__ == '__main__':
    outfile = ''
    infiles = []
    numInfs = 0
    bbox = None
    idx = 1
    while idx < len(sys.argv):
        if sys.argv[idx] == '-h' or sys.argv[idx] == '--help':
            usage()
            sys.exit(0)
        if sys.argv[idx] == '-o':
            if not idx + 1 < len(sys.argv):
                usage()
                sys.exit(1)
            outfile = sys.argv[idx + 1]
            idx += 2
            continue
        if sys.argv[idx] == '-bb':
            if not idx + 6 < len(sys.argv):
                usage()
                sys.exit(1)
            bbox = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
            bbox[0][0] = float(sys.argv[idx + 1])
            bbox[0][1] = float(sys.argv[idx + 2])
            bbox[0][2] = float(sys.argv[idx + 3])
            bbox[1][0] = float(sys.argv[idx + 4])
            bbox[1][1] = float(sys.argv[idx + 5])
            bbox[1][2] = float(sys.argv[idx + 6])
            idx += 7
            continue
        #infiles = infiles + [sys.argv[idx], ]
        #idx += 1
        #continue
        break

    infiles = reduce(operator.add, map(glob.glob, sys.argv[idx:]))
    numInfs = len(infiles)
    if len(outfile) < 4:
        print('%s: invalid outfile specified: %s' % (sys.argv[0], outfile))
        sys.exit(1)
    outSfx = outfile[-3:]
    if outSfx == 'vol' or outSfx == 'fdv':        # 4DVis
        ret = CreateFdvVol(outfile, infiles, bbox)
    elif outSfx == 'dat' or outSfx == 'avs':      # AVS
        ret = CreateAvsVol(outfile, infiles, bbox)
    elif outSfx == 'sph':      # Sphere
        ret = CreateSph(outfile, infiles, bbox)
    else:
        print('%s: unsupported outfile specified: %s' % (sys.argv[0], outfile))
        sys.exit(1)
    if ret != 0:
        sys.exit(1)

    sys.exit(ret)
