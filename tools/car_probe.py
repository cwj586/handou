# -*- coding: utf-8 -*-
import os, glob
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(BASE, 'assets', 'sprites', 'char-d811f16e', 'frames')
out = []

def probe(label, d, idxs):
    pngs = sorted(glob.glob(os.path.join(ROOT, d, '*.png')),
                  key=lambda p: int(os.path.splitext(os.path.basename(p))[0]))
    for i in idxs:
        im = Image.open(pngs[i])
        a = im.split()[3].point(lambda v: 255 if v >= 12 else 0)
        bb = a.getbbox()
        out.append('%-10s f%-3d W=%d H=%d bbox=%s' % (label, i, bb[2]-bb[0], bb[3]-bb[1], bb))

probe('enter',  'custom_local_923fa7c4232e-45faf64d-60e', [0, 1, 2, 3, 44, 45])
probe('exitcar','custom_003f7ed22da2496ba54551cde15f5947-cc547fa9-a99', [0, 1, 25, 26, 27, 28, 29])
probe('drive1', 'custom_db15bfe4c3a7443fa1b4c702fc696b80-2acf0953-c51', [0, 15])
probe('drive2', 'custom_90c89c48cb7c43658ced03183e48d54f-0a9a6a9c-79f', [0, 15])
probe('turn',   'custom_0a56412168c84e44bcea735120c9a733-32a73062-c50', [0, 2, 28])
probe('walk',   'custom_5dd819b8383e4173920398a8d3705ede-6e27a4b0-77d', [0])
io_ = open(os.path.join(BASE, 'out', 'car_probe.txt'), 'w', encoding='utf-8')
io_.write('\n'.join(out) + '\n')
io_.close()
print('done')
