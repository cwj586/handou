# -*- coding: utf-8 -*-
"""连点5次桌宠"""
import ctypes, time

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
cy = rc.b - 120
print('rect', rc.l, rc.t, rc.r, rc.b, 'click', cx, cy)
for i in range(5):
    u32.SetCursorPos(cx, cy)
    time.sleep(0.1)
    u32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    u32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(1.0)
print('clicked 5x')
