# -*- coding: utf-8 -*-
import json, io, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root = os.path.join(BASE, 'assets', 'sprites', 'char-d811f16e', 'video-runs')
out = io.open(os.path.join(BASE, 'out', 'runs_report.txt'), 'w', encoding='utf-8')
for d in sorted(os.listdir(root)):
    p = os.path.join(root, d, 'run.json')
    if not os.path.isfile(p):
        continue
    try:
        j = json.load(io.open(p, encoding='utf-8'))
        out.write('=== %s ===\n' % d)
        out.write(json.dumps(j, ensure_ascii=False)[:1500] + '\n\n')
    except Exception as e:
        out.write('%s ERR %s\n' % (d, e))
out.close()
print('done')
