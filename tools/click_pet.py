# -*- coding: utf-8 -*-
"""点击桌宠中心并截屏验证反应"""
import ctypes, time
from PIL import ImageGrab

ctypes.windll.user32.SetProcessDPIAware()
u32 = ctypes.windll.user32

hwnd = u32.FindWindowW(None, "BeanPet")
if not hwnd:
    print('NO WINDOW')
    raise SystemExit(1)

class RECT(ctypes.Structure):
    _fields_ = [('l', ctypes.c_long), ('t', ctypes.c_long), ('r', ctypes.c_long), ('b', ctypes.c_long)]

rc = RECT()
u32.GetWindowRect(hwnd, ctypes.byref(rc))
cx = (rc.l + rc.r) // 2
cy = rc.b - 120  # 角色身体位置(物理px)
print('rect', rc.l, rc.t, rc.r, rc.b, 'click at', cx, cy)

u32.SetCursorPos(cx, cy)
time.sleep(0.15)
u32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
time.sleep(0.05)
u32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
time.sleep(0.9)

im = ImageGrab.grab()
w, h = im.size
im.crop((0, int(h * 0.45), w, h)).save(r'C:\Users\Cwj\穹狼项目\憨豆\out\desk_click.png')
print('saved')
