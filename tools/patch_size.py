# -*- coding: utf-8 -*-
import io
p = r'C:\Users\Cwj\穹狼项目\憨豆\tools\preprocess_bean.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace('GLOBAL = 1.25', 'GLOBAL = 1.15')
s = s.replace('PERSON_TARGET = 290.0', 'PERSON_TARGET = 258.0')
io.open(p, 'w', encoding='utf-8').write(s)
print('patched size')
