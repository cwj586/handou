# -*- coding: utf-8 -*-
import json, io, os, glob
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(BASE, 'assets', 'sprites', 'char-d811f16e', 'frames')
OUT = os.path.join(BASE, 'out')

ACTIONS = {
    'walk':    'custom_5dd819b8383e4173920398a8d3705ede-6e27a4b0-77d',
    'run':     'custom_05179efa37c64c5c9ce07e3ed408a0f3-bdc0b9a0-5aa',
    'drive1':  'custom_db15bfe4c3a7443fa1b4c702fc696b80-2acf0953-c51',
    'drive2':  'custom_90c89c48cb7c43658ced03183e48d54f-0a9a6a9c-79f',
    'turn':    'custom_0a56412168c84e44bcea735120c9a733-32a73062-c50',
    'enter':   'custom_local_923fa7c4232e-45faf64d-60e',
    'exitcar': 'custom_003f7ed22da2496ba54551cde15f5947-cc547fa9-a99',
    'hit':     'custom_0c8aadc026e64d49b73c3287549a3538-e6a19a7d-817',
    'face':    'custom_2bf6e76c33854dc5aab2218c5009a2c6-90ce7dc9-60b',
    'takeout': 'custom_local_0f89f85e2db2-e1d1f733-fed',
    'dance1':  'custom_1805cc37a99c4e92bc57ab0cdaaf3341-91d53cdd-da7',
    'dance2':  'custom_1b2215e1ab4f469b95fb0cdbf1746ed4-26ce6fb9-12c',
    'putaway': 'custom_b17b558aa06b461abfa10020a6d1c7b3-83e8c2a9-c9a',
    'sitdown': 'custom_12d4b3ea37904094b8f20f66a9fd9bb5-e3b3b7dd-42d',
    'eat':     'custom_b51f74fbdb5d4c54a7c3985797741571-8cce5eb7-545',
    'rise':    'custom_local_8194f571cd82-1eb08fbe-a95',
}

manifest = {}
report = []
thumbs = []  # (key, first-frame RGBA thumbnail)

for key in sorted(ACTIONS):
    d = os.path.join(ROOT, ACTIONS[key])
    pngs = sorted(glob.glob(os.path.join(d, '*.png')), key=lambda p: int(os.path.splitext(os.path.basename(p))[0]))
    boxes = []
    for p in pngs:
        im = Image.open(p).convert('RGBA')
        bb = im.getbbox()  # based on alpha? getbbox uses non-zero; for RGBA includes alpha
        # use alpha channel explicitly, with threshold to kill noise
        a = im.split()[3].point(lambda v: 255 if v >= 12 else 0)
        bb = a.getbbox()
        boxes.append(list(bb) if bb else [0, 0, im.width, im.height])
        if len(boxes) == 1:
            first = im
    w, h = first.size
    manifest[key] = {
        'dir': ACTIONS[key],
        'n': len(pngs),
        'canvas': [w, h],
        'boxes': boxes,
    }
    hs = [b[3] - b[1] for b in boxes]
    ws = [b[2] - b[0] for b in boxes]
    bots = [b[3] for b in boxes]
    report.append('%-8s n=%2d canvas=%dx%d contentW=%d-%d contentH=%d-%d bottomInset=%d-%d' % (
        key, len(pngs), w, h, min(ws), max(ws), min(hs), max(hs), min(h - b for b in bots), max(h - b for b in bots)))
    # thumbnail: first frame + mid frame side by side, scaled to h=200
    mid_idx = len(pngs) // 2
    mid = Image.open(pngs[mid_idx]).convert('RGBA')
    th = 200
    f1 = first.resize((int(first.width * th / first.height), th), Image.LANCZOS)
    f2 = mid.resize((int(mid.width * th / mid.height), th), Image.LANCZOS)
    pair = Image.new('RGBA', (f1.width + f2.width + 2, th), (255, 0, 0, 255))
    pair.paste(f1, (0, 0), f1)
    pair.paste(f2, (f1.width + 2, 0), f2)
    thumbs.append((key, pair))

io.open(os.path.join(OUT, 'bean_frames_manifest.json'), 'w', encoding='utf-8').write(
    json.dumps(manifest, ensure_ascii=False))
io.open(os.path.join(OUT, 'measure_report.txt'), 'w', encoding='utf-8').write('\n'.join(report) + '\n')

# grid: 4 columns
cols = 4
cellw = max(t.width for _, t in thumbs) + 4
rows = (len(thumbs) + cols - 1) // cols
cellh = 200 + 4
grid = Image.new('RGBA', (cols * cellw, rows * cellh), (40, 40, 40, 255))
for i, (key, t) in enumerate(thumbs):
    r, c = divmod(i, cols)
    grid.paste(t, (c * cellw + 2, r * cellh + 2), t)
grid.convert('RGB').save(os.path.join(OUT, 'grid.png'))
# order file
io.open(os.path.join(OUT, 'grid_order.txt'), 'w', encoding='utf-8').write(
    '\n'.join('%d: %s' % (i, k) for i, (k, _) in enumerate(thumbs)) + '\n')
print('done')
