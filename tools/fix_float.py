# -*- coding: utf-8 -*-
import io
p = r'C:\Users\Cwj\穹狼项目\憨豆\tools\preprocess_bean.py'
s = io.open(p, encoding='utf-8').read()
bad1 = "    cxs = ','.join(('%.1f' % v) for v in CX)\n"
bad2 = "    gys = ','.join(('%.1f' % v) for v in GY)\n"
assert bad1 in s and bad2 in s
s = s.replace(bad1, "    cxs = ','.join(('%.1ff' % v) for v in CX)\n")
s = s.replace(bad2, "    gys = ','.join(('%.1ff' % v) for v in GY)\n")
io.open(p, 'w', encoding='utf-8').write(s)
print('fixed')
