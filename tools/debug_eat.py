# -*- coding: utf-8 -*-
import os, glob
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = os.path.join(BASE, 'assets', 'sprites', 'char-d811f16e', 'frames',
                 'custom_b51f74fbdb5d4c54a7c3985797741571-8cce5eb7-545')
out = []
for name in ('1.png', '15.png', '30.png'):
    im = Image.open(os.path.join(d, name)).convert('RGBA')
    a = im.split()[3]
    hist = a.histogram()
    out.append('%s size=%s alpha>0=%d alpha>=12=%d alpha>=40=%d' % (
        name, im.size, sum(hist[1:]), sum(hist[12:]), sum(hist[40:])))
    for th in (12, 40):
        b = a.point(lambda v: 255 if v >= th else 0).getbbox()
        out.append('  th=%d bbox=%s' % (th, b))
    # column profile: count of alpha>=40 per column band (16 bands)
    w, h = im.size
    band = w // 16
    prof = []
    px = a.load()
    for c in range(16):
        cnt = 0
        for x in range(c * band, min((c + 1) * band, w), 4):
            for y in range(0, h, 8):
                if px[x, y] >= 40:
                    cnt += 1
        prof.append(cnt)
    out.append('  colprofile=%s' % prof)
io_ = open(os.path.join(BASE, 'out', 'eat_debug.txt'), 'w', encoding='utf-8')
io_.write('\n'.join(out) + '\n')
io_.close()
print('done')
