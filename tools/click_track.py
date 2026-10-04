# -*- coding: utf-8 -*-
"""跟窗点击：每次点击前重新取窗口位置，点3次"""
import ctypes, time

ctypes.windll.user32.SetProcessDPIAware()
u32 = ctypes.windll.user32

class RECT(ctypes.Structure):
    _fields_ = [('l', ctypes.c_long), ('t', ctypes.c_long), ('r', ctypes.c_long), ('b', ctypes.c_long)]

for i in range(3):
    hwnd = u32.FindWindowW(None, "BeanPet")
    if not hwnd:
        print('NO WINDOW'); break
    rc = RECT()
    u32.GetWindowRect(hwnd, ctypes.byref(rc))
    cx = (rc.l + rc.r) // 2
    cy = rc.b - 120
    u32.SetCursorPos(cx, cy)
    time.sleep(0.05)
    u32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    u32.mouse_event(0x0004, 0, 0, 0, 0)
    print('click %d at %d,%d' % (i, cx, cy))
    time.sleep(1.2)
