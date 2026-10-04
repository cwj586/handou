# -*- coding: utf-8 -*-
import json, io, os, glob

BASE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.dirname(BASE)
out = io.open(os.path.join(OUTDIR, 'out', 'anim_report.txt'), 'w', encoding='utf-8')

root = os.path.join(OUTDIR, 'assets', 'sprites', 'char-d811f16e')

# 1) one anim.json sample structure
with io.open(os.path.join(root, 'custom_5dd819b8383e4173920398a8d3705ede.anim.json'), encoding='utf-8') as f:
    a = json.load(f)
out.write('ANIM JSON KEYS: %r\n' % (list(a.keys()),))
out.write(json.dumps(a, ensure_ascii=False, indent=1)[:2000] + '\n\n')

# 2) action json
with io.open(os.path.join(root, 'custom_5dd819b8383e4173920398a8d3705ede.json'), encoding='utf-8') as f:
    b = json.load(f)
out.write('ACTION JSON:\n')
out.write(json.dumps(b, ensure_ascii=False, indent=1)[:1500] + '\n\n')

# 3) list all actions + frame counts + frame sizes
out.write('=== ALL ACTIONS ===\n')
frames_dir = os.path.join(root, 'frames')
for d in sorted(os.listdir(frames_dir)):
    p = os.path.join(frames_dir, d)
    if not os.path.isdir(p):
        continue
    pngs = sorted(glob.glob(os.path.join(p, '*.png')))
    if not pngs:
        continue
    from PIL import Image
    im = Image.open(pngs[0])
    # sample middle frame size too
    mid = pngs[len(pngs)//2]
    im2 = Image.open(mid)
    out.write('%s  n=%d  size0=%s sizeMid=%s\n' % (d, len(pngs), im.size, im2.size))

out.close()
print('done')
