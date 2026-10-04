# -*- coding: utf-8 -*-
"""走路只取片段1-24帧，跑步只取4-25帧"""
import io
p = r'C:\Users\Cwj\穹狼项目\憨豆\tools\preprocess_bean.py'
s = io.open(p, encoding='utf-8').read()

old_w = "    'walk':    ('custom_5dd819b8383e4173920398a8d3705ede-6e27a4b0-77d', None, 1.0, 'person'),"
new_w = "    'walk':    ('custom_5dd819b8383e4173920398a8d3705ede-6e27a4b0-77d', list(range(0, 24)), 1.0, 'person'),  # 片段1-24帧"
assert old_w in s
s = s.replace(old_w, new_w)

old_r = "    'run':     ('custom_05179efa37c64c5c9ce07e3ed408a0f3-bdc0b9a0-5aa', None, 1.0, 'person'),"
new_r = "    'run':     ('custom_05179efa37c64c5c9ce07e3ed408a0f3-bdc0b9a0-5aa', list(range(3, 25)), 1.0, 'person'),  # 片段4-25帧"
assert old_r in s
s = s.replace(old_r, new_r)

old_loop = """for key in CLIPS:
    src = load_frames(key)
    bx = boxes_of(src)
    if key == 'stand':
        src = [src[0]]; bx = [bx[0]]
    if key == 'rest':
        continue
    generated[key] = emit(key, src, bx, scales[key])"""
new_loop = """for key in CLIPS:
    src = load_frames(key)
    bx = boxes_of(src)
    idxs = CLIPS[key][1]
    if idxs is not None:
        src = [src[i] for i in idxs]
        bx = [bx[i] for i in idxs]
    if key == 'rest':
        continue
    generated[key] = emit(key, src, bx, scales[key])"""
assert old_loop in s
s = s.replace(old_loop, new_loop)

io.open(p, 'w', encoding='utf-8').write(s)
print('patched frame ranges')
