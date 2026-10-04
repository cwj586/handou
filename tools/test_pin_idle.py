# -*- coding: utf-8 -*-
# 驻留待机验证: 双击后窗口应停在右缘不动, 期间原地走/跑/开车
import ctypes, time, sys
from ctypes import wintypes

LOG = r"C:\Users\Cwj\穹狼项目\憨豆\pet\bin\beanpet.log"
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()

MOUSEEVENTF_MOVE = 0x0001; MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002; MOUSEEVENTF_LEFTUP = 0x0004

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))]

class INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT), ("pad", ctypes.c_byte * 32)]
    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _U)]

def mouse(flags, dx=0, dy=0):
    inp = INPUT(type=0)
    inp.mi = MOUSEINPUT(dx, dy, 0, flags, 0, None)
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

def abs_move(x, y):
    sx = user32.GetSystemMetrics(0); sy = user32.GetSystemMetrics(1)
    mouse(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, int(x * 65535 / sx), int(y * 65535 / sy))

def dblclick(x, y):
    abs_move(x, y); time.sleep(0.15)
    for _ in range(2):
        mouse(MOUSEEVENTF_LEFTDOWN); time.sleep(0.05); mouse(MOUSEEVENTF_LEFTUP); time.sleep(0.12)

def pet_rect():
    h = user32.FindWindowW(None, "BeanPet")
    if not h: return None
    r = wintypes.RECT()
    user32.GetWindowRect(h, ctypes.byref(r))
    return (r.left, r.top, r.right, r.bottom)

def pet_center():
    r = pet_rect()
    return ((r[0] + r[2]) // 2, (r[1] + r[3]) // 2) if r else None

def log_lines():
    with open(LOG, encoding="utf-8", errors="ignore") as f:
        return f.read().splitlines()

cx, cy = pet_center()
n0 = len(log_lines())
dblclick(cx, cy)
t0 = time.time()
pinned = False
while time.time() - t0 < 15:
    if any("pinned at right edge" in ln for ln in log_lines()[n0:]): pinned = True; break
    time.sleep(0.3)
print("pinned:", pinned)
if not pinned: sys.exit(1)

xs = []
for i in range(24):
    r = pet_rect()
    xs.append(r[0])
    time.sleep(0.5)
print("window left samples:", xs)
print("X moved px:", max(xs) - min(xs))

n1 = len(log_lines())
print("---- 驻留期间日志 ----")
for ln in log_lines()[n0:n1]:
    print(ln)

cx, cy = pet_center()
n2 = len(log_lines())
dblclick(cx, cy)
t0 = time.time()
unpinned = False
while time.time() - t0 < 6:
    if any("unpin" in ln for ln in log_lines()[n2:]): unpinned = True; break
    time.sleep(0.3)
print("unpin:", unpinned)
print("RESULT:", "PASS" if (pinned and unpinned and max(xs) - min(xs) <= 2) else "FAIL")
