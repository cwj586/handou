# -*- coding: utf-8 -*-
import io

p = r'C:\Users\Cwj\穹狼项目\憨豆\tools\preprocess_bean.py'
s = io.open(p, encoding='utf-8').read()
i = s.find('for key in sorted(generated):')
j = s.find('os.makedirs(PET, exist_ok=True)')
assert i > 0 and j > i, (i, j)
new = (
    "for key in sorted(generated):\n"
    "    files, W, H, CX, GY = generated[key]\n"
    "    fs = ',\\n                    '.join('\"%s\"' % f for f in files)\n"
    "    ws = ','.join(str(v) for v in W)\n"
    "    hs = ','.join(str(v) for v in H)\n"
    "    cxs = ','.join(('%.1f' % v) for v in CX)\n"
    "    gys = ','.join(('%.1f' % v) for v in GY)\n"
    "    A('            L.Add(new BeanAction(\"%s\", new string[] {' % key))\n"
    "    A(fs)\n"
    "    A('                },')\n"
    "    A('                new int[] {%s},' % ws)\n"
    "    A('                new int[] {%s},' % hs)\n"
    "    A('                new float[] {%s},' % cxs)\n"
    "    A('                new float[] {%s}));' % gys)\n"
    "A('            return L;')\n"
    "A('        }')\n"
    "A('    }')\n"
    "A('}')\n"
    "\n"
)
s = s[:i] + new + s[j:]
io.open(p, 'w', encoding='utf-8').write(s)
print('patched')
