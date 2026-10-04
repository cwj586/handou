# -*- coding: utf-8 -*-
import ctypes, sys
from PIL import ImageGrab

ctypes.windll.user32.SetProcessDPIAware()
out = r'C:\Users\Cwj\穹狼项目\憨豆\out\desk.png'
im = ImageGrab.grab()
# 裁剪下半屏(桌宠活动区)，减小文件
w, h = im.size
im.crop((0, int(h * 0.45), w, h)).save(out)
print('saved', im.size)
