# -*- coding: utf-8 -*-
"""exitcar 改按人物归一 + 生成 ExitZoom 常量（开车->下车的车尺寸渐变比）"""
import io
p = r'C:\Users\Cwj\穹狼项目\憨豆\tools\preprocess_bean.py'
s = io.open(p, encoding='utf-8').read()

# 1) exitcar 覆盖为人物归一（末帧=站立的人）
old = "CAR_REF_FRAME = {'drive2': 0, 'turn': 0, 'exitcar': 0, 'enter': -1}  # -1=末帧(整车)"
new = "CAR_REF_FRAME = {'drive2': 0, 'turn': 0, 'enter': -1}  # -1=末帧(整车)"
assert old in s
s = s.replace(old, new)

old2 = "scales['drive1'] = CAR_TARGET / float(max(b[3] - b[1] for b in boxes_of(load_frames('drive1'))))"
new2 = old2 + "\n# exitcar 特例：按末帧站立人物归一（该素材内部人:车比例画错，人308 vs 车258）\n" \
             "scales['exitcar'] = PERSON_TARGET / float(content_h('exitcar', len(load_frames('exitcar')) - 1))"
assert old2 in s
s = s.replace(old2, new2)

# 2) WIN 尺寸把 exitcar 放大回归(渐变期间)也算进去，并输出 ExitZoom
old3 = """maxw = max(max(generated[k][1]) for k in generated)
maxh = max(max(generated[k][2]) for k in generated)
pad = 26
WIN_W = maxw + pad
WIN_H = maxh + pad + 30
rep.append('maxCrop=%dx%d  WIN=%dx%d' % (maxw, maxh, WIN_W, WIN_H))"""
new3 = """maxw = max(max(generated[k][1]) for k in generated)
maxh = max(max(generated[k][2]) for k in generated)
EXIT_ZOOM = 1.0 / scales['exitcar']   # 开车段车尺寸 -> 下车段车尺寸 的渐变起点倍率
ew = max(generated['exitcar'][1]) * EXIT_ZOOM
eh = max(generated['exitcar'][2]) * EXIT_ZOOM
pad = 26
WIN_W = int(max(maxw, ew)) + pad
WIN_H = int(max(maxh, eh)) + pad + 30
rep.append('maxCrop=%dx%d exitZoom=%.4f WIN=%dx%d' % (maxw, maxh, EXIT_ZOOM, WIN_W, WIN_H))"""
assert old3 in s
s = s.replace(old3, new3)

# 3) g.cs 输出 ExitZoom
old4 = "A('        public const int Fps = %d;' % FPS)"
new4 = old4 + "\nA('        public const double ExitZoom = %.4f;' % EXIT_ZOOM)"
assert old4 in s
s = s.replace(old4, new4)

io.open(p, 'w', encoding='utf-8').write(s)
print('patched exitcar')
