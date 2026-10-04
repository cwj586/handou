# -*- coding: utf-8 -*-
import os
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = os.path.join(BASE, 'assets', 'sprites', 'char-d811f16e', 'frames',
                 'custom_b51f74fbdb5d4c54a7c3985797741571-8cce5eb7-545')
out = []
for name in ('1.png', '15.png'):
    im = Image.open(os.path.join(d, name)).convert('RGBA')
    px = im.load()
    w, h = im.size
    pts = [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3), (w // 2, h // 2), (w // 2, 160), (60, 300), (700, 300), (386, 500)]
    out.append(name + ' ' + ' '.join('%s=%s' % (p, px[p]) for p in pts))
# unique colors sample count
im = Image.open(os.path.join(d, '15.png')).convert('RGB')
cols = im.getcolors(200000)
cols.sort(reverse=True)
out.append('top colors: ' + ' '.join('%d:%s' % (n, c) for n, c in cols[:12]))
io_ = open(os.path.join(BASE, 'out', 'eat_debug2.txt'), 'w', encoding='utf-8')
io_.write('\n'.join(out) + '\n')
io_.close()
print('done')
