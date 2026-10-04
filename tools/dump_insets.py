# -*- coding: utf-8 -*-
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
m = json.load(open(os.path.join(BASE, 'out', 'bean_frames_manifest.json'), encoding='utf-8'))
out = []
for key in ('enter', 'exitcar', 'hit', 'dance2', 'rise', 'sitdown', 'walk', 'drive1', 'drive2', 'turn'):
    a = m[key]
    w, h = a['canvas']
    ins = [h - b[3] for b in a['boxes']]
    out.append('%s (%d frames, canvas %dx%d):' % (key, a['n'], w, h))
    out.append('  insets: ' + ','.join(str(i) for i in ins))
io_ = open(os.path.join(BASE, 'out', 'insets.txt'), 'w', encoding='utf-8')
io_.write('\n'.join(out) + '\n')
io_.close()
print('done')
