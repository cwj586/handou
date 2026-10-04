# -*- coding: utf-8 -*-
import io
p = r'C:\Users\Cwj\穹狼项目\憨豆\tools\preprocess_bean.py'
s = io.open(p, encoding='utf-8').read()
bad = "    A('            L.Add(new BeanAction(\"%s\", new string[] {' % key))\n"
good = "    A('            L.Add(new BeanAction(\"%s\", new string[] {' % key)\n"
assert bad in s
s = s.replace(bad, good)
io.open(p, 'w', encoding='utf-8').write(s)
print('fixed')
