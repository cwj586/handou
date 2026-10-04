# -*- coding: utf-8 -*-
"""憨豆桌宠帧预处理：裁剪->归一化->1.25x LANCZOS放大->锐化->输出帧+BeanFrames.g.cs"""
import json, os, glob
from PIL import Image, ImageFilter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(BASE, 'assets', 'sprites', 'char-d811f16e', 'frames')
PET = os.path.join(BASE, 'pet')
FRAMES_OUT = os.path.join(PET, 'assets', 'frames')
MARGIN = 8          # 裁剪外边距(原始px)
GLOBAL = 0.8        # 全局放大（1.0=原素材大小）
THRESH = 12
FPS = 15

CLIPS = {
    'stand':   ('custom_5dd819b8383e4173920398a8d3705ede-6e27a4b0-77d', [0], 1.0, 'person'),
    'walk':    ('custom_5dd819b8383e4173920398a8d3705ede-6e27a4b0-77d', list(range(0, 24)), 1.0, 'person'),  # 片段1-24帧
    'run':     ('custom_05179efa37c64c5c9ce07e3ed408a0f3-bdc0b9a0-5aa', list(range(3, 25)), 1.0, 'person'),  # 片段4-25帧
    'drive1':  ('custom_db15bfe4c3a7443fa1b4c702fc696b80-2acf0953-c51', None, None, 'car'),
    'drive2':  ('custom_90c89c48cb7c43658ced03183e48d54f-0a9a6a9c-79f', None, None, 'car'),
    'turn':    ('custom_0a56412168c84e44bcea735120c9a733-32a73062-c50', None, None, 'car'),
    'enter':   ('custom_local_923fa7c4232e-45faf64d-60e', None, None, 'car'),
    'exitcar': ('custom_003f7ed22da2496ba54551cde15f5947-cc547fa9-a99', None, None, 'car'),
    'hit':     ('custom_0c8aadc026e64d49b73c3287549a3538-e6a19a7d-817', None, None, 'person'),
    'face':    ('custom_2bf6e76c33854dc5aab2218c5009a2c6-90ce7dc9-60b', None, None, 'person'),
    'takeout': ('custom_local_0f89f85e2db2-e1d1f733-fed', None, None, 'person'),
    'dance1':  ('custom_1805cc37a99c4e92bc57ab0cdaaf3341-91d53cdd-da7', None, None, 'person'),
    'dance2':  ('custom_1b2215e1ab4f469b95fb0cdbf1746ed4-26ce6fb9-12c', None, None, 'person'),
    'putaway': ('custom_b17b558aa06b461abfa10020a6d1c7b3-83e8c2a9-c9a', None, None, 'person'),
    'sitdown': ('custom_12d4b3ea37904094b8f20f66a9fd9bb5-e3b3b7dd-42d', None, None, 'person'),
}

def load_frames(key):
    d = os.path.join(ROOT, CLIPS[key][0])
    pngs = sorted(glob.glob(os.path.join(d, '*.png')),
                  key=lambda p: int(os.path.splitext(os.path.basename(p))[0]))
    return pngs

def boxes_of(pngs):
    out = []
    for p in pngs:
        im = Image.open(p)
        a = im.split()[3].point(lambda v: 255 if v >= THRESH else 0)
        bb = a.getbbox()
        out.append(bb if bb else (0, 0, im.width, im.height))
    return out

def content_h(key, idx):
    pngs = load_frames(key)
    bb = boxes_of(pngs)[idx]
    return bb[3] - bb[1]

# ---- 归一化比例：人物统一站高 / 汽车统一车高 ----
PERSON_TARGET = 258.0   # 站立人物目标高(原始px)，介于各段素材之间
CAR_TARGET = 258.0      # 汽车目标高 = 与人物一致(解决开车段偏大)

# 各片段"参考帧"实测内容高(站立人物或整车)
REF_H = {
    'walk': 258, 'run': 258, 'stand': 258,
    'hit': 280, 'face': 283, 'takeout': 283,
    'dance1': 283, 'dance2': 277,
    'putaway': 380,          # 尾帧站立(本段人物天生偏大)
    'sitdown': 250,          # 首帧站立(沙发弹出前)
}
CAR_REF_FRAME = {'drive2': 0, 'turn': 0, 'enter': -1}  # -1=末帧(整车)

scales = {}
for k, h in REF_H.items():
    scales[k] = PERSON_TARGET / float(h)
for k, idx in CAR_REF_FRAME.items():
    pngs = load_frames(k)
    i = len(pngs) - 1 if idx < 0 else idx
    h = content_h(k, i)
    scales[k] = CAR_TARGET / float(h)
scales['drive1'] = CAR_TARGET / float(max(b[3] - b[1] for b in boxes_of(load_frames('drive1'))))
# exitcar 特例：按末帧站立人物归一（该素材内部人:车比例画错，人308 vs 车258）
scales['exitcar'] = PERSON_TARGET / float(content_h('exitcar', len(load_frames('exitcar')) - 1))
rep = ['PERSON_TARGET=%.0f CAR_TARGET=%.0f' % (PERSON_TARGET, CAR_TARGET)]
for k in sorted(scales):
    rep.append('%-8s scale=%.3f' % (k, scales[k]))

# ---- 输出 ----
if os.path.isdir(FRAMES_OUT):
    import shutil
    shutil.rmtree(FRAMES_OUT)
os.makedirs(FRAMES_OUT)

def emit(key, src_pngs, src_boxes, scale):
    S = scale * GLOBAL
    outdir = os.path.join(FRAMES_OUT, key)
    os.makedirs(outdir)
    files, W, H, CX, GY = [], [], [], [], []
    for i, p in enumerate(src_pngs):
        im = Image.open(p).convert('RGBA')
        x0, y0, x1, y1 = src_boxes[i]
        cx0 = max(0, x0 - MARGIN); cy0 = max(0, y0 - MARGIN)
        cx1 = min(im.width, x1 + MARGIN); cy1 = min(im.height, y1 + MARGIN)
        crop = im.crop((cx0, cy0, cx1, cy1))
        nw = max(1, int(round(crop.width * S)))
        nh = max(1, int(round(crop.height * S)))
        crop = crop.resize((nw, nh), Image.LANCZOS)
        if S > 1.02:
            crop = crop.filter(ImageFilter.UnsharpMask(radius=2, percent=55, threshold=2))
        # 内容在裁剪帧内的几何(缩放后)
        ccx = ((x0 + x1) / 2.0 - cx0) * S
        gbottom = (y1 - cy0) * S
        name = '%s_%03d.png' % (key, i)
        crop.save(os.path.join(outdir, name))
        files.append('%s/%s' % (key, name))
        W.append(nw); H.append(nh)
        CX.append(round(ccx, 1)); GY.append(round(gbottom, 1))
    return files, W, H, CX, GY

generated = {}
for key in CLIPS:
    src = load_frames(key)
    bx = boxes_of(src)
    idxs = CLIPS[key][1]
    if idxs is not None:
        src = [src[i] for i in idxs]
        bx = [bx[i] for i in idxs]
    if key == 'rest':
        continue
    generated[key] = emit(key, src, bx, scales[key])
    rep.append('%-8s emit %d frames' % (key, len(generated[key][0])))

# rest = sitdown 呼吸段 ping-pong（结束落在近29帧）；standup = sitdown 整段倒放（起身）
sit_pngs = load_frames('sitdown')
sit_bx = boxes_of(sit_pngs)
idxs = list(range(18, 30)) + list(range(28, 18, -1))
rest_pngs = [sit_pngs[i] for i in idxs]
rest_bx = [sit_bx[i] for i in idxs]
generated['rest'] = emit('rest', rest_pngs, rest_bx, scales['sitdown'])
rep.append('rest    emit %d frames (sitdown 18-29 pingpong)' % len(generated['rest'][0]))

gen_pngs = list(reversed(sit_pngs))
gen_bx = list(reversed(sit_bx))
generated['standup'] = emit('standup', gen_pngs, gen_bx, scales['sitdown'])
rep.append('standup emit %d frames (sitdown reversed)' % len(generated['standup'][0]))

maxw = max(max(generated[k][1]) for k in generated)
maxh = max(max(generated[k][2]) for k in generated)
EXIT_ZOOM = 1.0 / scales['exitcar']   # 开车段车尺寸 -> 下车段车尺寸 的渐变起点倍率
ew = max(generated['exitcar'][1]) * EXIT_ZOOM
eh = max(generated['exitcar'][2]) * EXIT_ZOOM
pad = 26
WIN_W = int(max(maxw, ew)) + pad
WIN_H = int(max(maxh, eh)) + pad + 30
rep.append('maxCrop=%dx%d exitZoom=%.4f WIN=%dx%d' % (maxw, maxh, EXIT_ZOOM, WIN_W, WIN_H))

# ---- BeanFrames.g.cs ----
lines = []
A = lines.append
A('// 自动生成：tools/preprocess_bean.py')
A('using System.Collections.Generic;')
A('')
A('namespace BeanPet')
A('{')
A('    public static class BeanFrames')
A('    {')
A('        public const int WinW = %d;  // 物理像素' % WIN_W)
A('        public const int WinH = %d;' % WIN_H)
A('        public const int Fps = %d;' % FPS)
A('        public const double ExitZoom = %.4f;' % EXIT_ZOOM)
A('')
A('        public static List<BeanAction> Build()')
A('        {')
A('            var L = new List<BeanAction>();')
for key in sorted(generated):
    files, W, H, CX, GY = generated[key]
    fs = ',\n                    '.join('"%s"' % f for f in files)
    ws = ','.join(str(v) for v in W)
    hs = ','.join(str(v) for v in H)
    cxs = ','.join(('%.1ff' % v) for v in CX)
    gys = ','.join(('%.1ff' % v) for v in GY)
    A('            L.Add(new BeanAction("%s", new string[] {' % key)
    A(fs)
    A('                },')
    A('                new int[] {%s},' % ws)
    A('                new int[] {%s},' % hs)
    A('                new float[] {%s},' % cxs)
    A('                new float[] {%s}));' % gys)
A('            return L;')
A('        }')
A('    }')
A('}')

os.makedirs(PET, exist_ok=True)
with open(os.path.join(PET, 'BeanFrames.g.cs'), 'w', encoding='utf-8-sig') as f:
    f.write('\n'.join(lines) + '\n')

io_ = open(os.path.join(BASE, 'out', 'preprocess_report.txt'), 'w', encoding='utf-8')
io_.write('\n'.join(rep) + '\n')
io_.close()
print('done')
