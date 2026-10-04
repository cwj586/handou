# -*- coding: utf-8 -*-
import os, glob
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(BASE, 'assets', 'sprites', 'char-d811f16e', 'frames')

ROWS = [
    ('walk',    'custom_5dd819b8383e4173920398a8d3705ede-6e27a4b0-77d'),
    ('run',     'custom_05179efa37c64c5c9ce07e3ed408a0f3-bdc0b9a0-5aa'),
    ('drive1',  'custom_db15bfe4c3a7443fa1b4c702fc696b80-2acf0953-c51'),
    ('drive2',  'custom_90c89c48cb7c43658ced03183e48d54f-0a9a6a9c-79f'),
    ('turn',    'custom_0a56412168c84e44bcea735120c9a733-32a73062-c50'),
    ('enter',   'custom_local_923fa7c4232e-45faf64d-60e'),
    ('exitcar', 'custom_003f7ed22da2496ba54551cde15f5947-cc547fa9-a99'),
]

CELL_W, CELL_H, GAP = 280, 215, 6
sheet = Image.new('RGB', (4 * (CELL_W + GAP) + GAP, len(ROWS) * (CELL_H + GAP) + GAP), (30, 30, 60))
for r, (key, d) in enumerate(ROWS):
    pngs = sorted(glob.glob(os.path.join(ROOT, d, '*.png')),
                  key=lambda p: int(os.path.splitext(os.path.basename(p))[0]))
    n = len(pngs)
    idxs = [0, n // 4, n // 2, (3 * n) // 4]
    for c, fi in enumerate(idxs):
        im = Image.open(pngs[fi]).convert('RGBA')
        a = im.split()[3].point(lambda v: 255 if v >= 12 else 0)
        bb = a.getbbox()
        im = im.crop(bb)
        s = min(CELL_W / im.width, CELL_H / im.height)
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
        cell = Image.new('RGB', (CELL_W, CELL_H), (200, 60, 60))
        cell.paste(im, ((CELL_W - im.width) // 2, (CELL_H - im.height) // 2), im)
        sheet.paste(cell, (GAP + c * (CELL_W + GAP), GAP + r * (CELL_H + GAP)))
sheet.save(os.path.join(BASE, 'out', 'grid2.png'))
print('done')
