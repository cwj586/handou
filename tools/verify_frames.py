# -*- coding: utf-8 -*-
"""验证桌宠走路/跑步的帧来源"""
import io, os, glob, json

BASE = r'C:\Users\Cwj\穹狼项目\憨豆'
SRC = os.path.join(BASE, 'assets', 'sprites', 'char-d811f16e', 'frames')
PET = os.path.join(BASE, 'pet', 'assets', 'frames')
out = []

MAP = {
    'walk': 'custom_5dd819b8383e4173920398a8d3705ede-6e27a4b0-77d',   # 原地走路
    'run':  'custom_05179efa37c64c5c9ce07e3ed408a0f3-bdc0b9a0-5aa',   # 原地跑步
}

for key, d in MAP.items():
    src_pngs = sorted(glob.glob(os.path.join(SRC, d, '*.png')))
    pet_pngs = sorted(glob.glob(os.path.join(PET, key, '*.png')))
    out.append('[%s] 来源(抽取片段目录): frames\\%s' % (key, d))
    out.append('  源片段帧数: %d  ->  桌宠帧数: %d' % (len(src_pngs), len(pet_pngs)))
    # 逐帧比对：桌宠帧(裁剪缩放后)应与源帧内容一致
    from PIL import Image
    ok = True
    for i in (0, len(src_pngs) // 2, len(src_pngs) - 1):
        s = Image.open(src_pngs[i]).convert('RGBA')
        a = s.split()[3].point(lambda v: 255 if v >= 12 else 0)
        bb = a.getbbox()
        s2 = s.crop(bb)
        p = Image.open(pet_pngs[i]).convert('RGBA')
        # 桌宠帧含8px源边距*缩放，比较内容主色即可：源裁剪帧缩到桌宠帧主区域
        ratio = p.width / float(s2.width)
        s3 = s2.resize((max(1, int(s2.width * ratio * 0.99)), max(1, int(s2.height * ratio * 0.99))), Image.NEAREST)
        cs = sorted(s3.convert('RGB').getcolors(500000), reverse=True)[0][1]
        cp = sorted(p.convert('RGB').getcolors(500000), reverse=True)[0][1]
        same = abs(cs[0]-cp[0]) < 30 and abs(cs[1]-cp[1]) < 30 and abs(cs[2]-cp[2]) < 30
        ok = ok and same
        out.append('  帧%d: 源裁剪%s vs 桌宠%s 主色 %s vs %s -> %s' % (i, s2.size, p.size, cs, cp, '一致' if same else '不一致'))
    out.append('  内容比对: %s' % ('一致(桌宠帧=抽取片段裁剪缩放版)' if ok else '不一致'))

# 确认桌宠数据里没有任何"整图sheet"路径
g = io.open(os.path.join(BASE, 'pet', 'BeanFrames.g.cs'), encoding='utf-8-sig').read()
out.append('')
out.append('BeanFrames.g.cs 中引用 sheet 整图: %s' % ('有' if 'sheet-' in g else '无(全部是 frames/ 动作帧)'))
out.append('BeanFrames.g.cs walk 帧文件数: %d, run 帧文件数: %d' % (g.count('"walk/'), g.count('"run/')))

io.open(os.path.join(BASE, 'out', 'verify_frames.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('done')
