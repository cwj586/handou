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
        if i >= len(pngs):
            continue
        im = Image.open(pngs[i])
        a = im.split()[3].point(lambda v: 255 if v >= 12 else 0)
        bb = a.getbbox()
        out.append('%-10s f%-3d canvas=%s bbox=%s W=%d H=%d' % (
            label, i, im.size, bb, bb[2] - bb[0], bb[3] - bb[1]))

probe('sitdown', 'custom_12d4b3ea37904094b8f20f66a9fd9bb5-e3b3b7dd-42d', [0, 1, 5, 15, 29])
probe('rise', 'custom_local_8194f571cd82-1eb08fbe-a95', [0, 5, 15, 25, 28, 30])
probe('putaway', 'custom_b17b558aa06b461abfa10020a6d1c7b3-83e8c2a9-c9a', [0, 5, 15, 25, 29])
probe('hit', 'custom_0c8aadc026e64d49b73c3287549a3538-e6a19a7d-817', [0, 30, 44])
probe('face', 'custom_2bf6e76c33854dc5aab2218c5009a2c6-90ce7dc9-60b', [0, 29])
probe('takeout', 'custom_local_0f89f85e2db2-e1d1f733-fed', [0, 30])
probe('dance1', 'custom_1805cc37a99c4e92bc57ab0cdaaf3341-91d53cdd-da7', [0, 59])
probe('dance2', 'custom_1b2215e1ab4f469b95fb0cdbf1746ed4-26ce6fb9-12c', [0, 44])
io_ = open(os.path.join(BASE, 'out', 'ref_probe.txt'), 'w', encoding='utf-8')
io_.write('\n'.join(out) + '\n')
io_.close()
print('done')
