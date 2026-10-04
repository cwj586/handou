# -*- coding: utf-8 -*-
import io
p = r'C:\Users\Cwj\穹狼项目\憨豆\tools\preprocess_bean.py'
s = io.open(p, encoding='utf-8').read()

# 车与人物统一：汽车目标高 = 人物目标高 = 258
s = s.replace('CAR_TARGET = 310.0      # 汽车目标高 = drive1 车高',
              'CAR_TARGET = 258.0      # 汽车目标高 = 与人物一致(解决开车段偏大)')
# drive1 也要按目标车高缩，不再恒为1.0
s = s.replace("scales['drive1'] = 1.0",
              "scales['drive1'] = CAR_TARGET / float(max(b[3] - b[1] for b in boxes_of(load_frames('drive1'))))")
io.open(p, 'w', encoding='utf-8').write(s)
print('patched car scale')
