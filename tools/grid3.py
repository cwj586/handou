# -*- coding: utf-8 -*-
import os, glob
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(BASE, 'assets', 'sprites', 'char-d811f16e', 'frames')
PICKS = [
    ('enter_f40',  'custom_local_923fa7c4232e-45faf64d-60e', 40),
    ('enter_f0',   'custom_local_923fa7c4232e-45faf64d-60e', 0),
    ('exit_f0',    'custom_003f7ed22da2496ba54551cde15f5947-cc547fa9-a99', 0),
    ('exit_f26',   'custom_003f7ed22da2496ba54551cde15f5947-cc547fa9-a99', 26),
]
GAP = 8
cells = []
for label, d, fi in PICKS:
    pngs = sorted(glob.glob(os.path.join(ROOT, d, '*.png')),
                  key=lambda p: int(os.path.splitext(os.path.basename(p))[0]))
    im = Image.open(pngs[fi]).convert('RGBA')
    a = im.split()[3].point(lambda v: 255 if v >= 12 else 0)
    bb = a.getbbox()
    im = im.crop(bb)
    cells.append((label, im))
W = max(im.width for _, im in cells)
H = sum(im.height for _, im in cells) + GAP * (len(cells) + 1)
sheet = Image.new('RGB', (W + 2 * GAP, H), (30, 30, 60))
y = GAP
for label, im in cells:
    sheet.paste(im, (GAP, y), im)
    y += im.height + GAP
sheet.save(os.path.join(BASE, 'out', 'grid3.png'))
print('done', sheet.size)
