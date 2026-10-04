# -*- coding: utf-8 -*-
import os, glob
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(BASE, 'assets', 'sprites', 'char-d811f16e', 'frames')

def frames_of(d):
    return sorted(glob.glob(os.path.join(ROOT, d, '*.png')),
                  key=lambda p: int(os.path.splitext(os.path.basename(p))[0]))

PICKS = [
    ('sit_f0',  frames_of('custom_12d4b3ea37904094b8f20f66a9fd9bb5-e3b3b7dd-42d')[0]),
    ('sit_f6',  frames_of('custom_12d4b3ea37904094b8f20f66a9fd9bb5-e3b3b7dd-42d')[6]),
    ('sit_f29', frames_of('custom_12d4b3ea37904094b8f20f66a9fd9bb5-e3b3b7dd-42d')[29]),
    ('rise_f25', frames_of('custom_local_8194f571cd82-1eb08fbe-a95')[25]),
]
GAP = 6
cells = []
for label, p in PICKS:
    im = Image.open(p).convert('RGBA')
    a = im.split()[3].point(lambda v: 255 if v >= 12 else 0)
    bb = a.getbbox()
    cells.append(im.crop(bb))
W = max(im.width for im in cells)
H = sum(im.height for im in cells) + GAP * (len(cells) + 1)
sheet = Image.new('RGB', (W + 2 * GAP, H), (30, 30, 60))
y = GAP
for im in cells:
    sheet.paste(im, (GAP, y), im)
    y += im.height + GAP
sheet.save(os.path.join(BASE, 'out', 'grid4.png'))
print('done', sheet.size)
