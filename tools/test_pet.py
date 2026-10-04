# -*- coding: utf-8 -*-
# 憨豆桌宠交互冒烟测试: 双击驻留 -> 双击解除 -> 拖拽
import ctypes, time, sys
from ctypes import wintypes

LOG = r"C:\Users\Cwj\穹狼项目\憨豆\pet\bin\beanpet.log"
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

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

def click(x, y):
    abs_move(x, y); time.sleep(0.15)
    mouse(MOUSEEVENTF_LEFTDOWN); time.sleep(0.05); mouse(MOUSEEVENTF_LEFTUP)

def dblclick(x, y):
    click(x, y); time.sleep(0.12); click(x, y)

def pet_rect():
    h = user32.FindWindowW(None, "BeanPet")
    if not h: return None, None
    r = wintypes.RECT()
    user32.GetWindowRect(h, ctypes.byref(r))
    return (r.left + r.right) // 2, (r.top + r.bottom) // 2

def log_lines():
    with open(LOG, encoding="utf-8", errors="ignore") as f:
        return f.read().splitlines()

def wait_for(n0, keyword, timeout):
    t0 = time.time()
    while time.time() - t0 < timeout:
        for ln in log_lines()[n0:]:
            if keyword in ln: return ln
        time.sleep(0.3)
    return None

ok = True
def check(name, r):
    global ok
    print(("PASS" if r else "FAIL") + " " + name + ": " + str(r))
    if not r: ok = False

# 1) 双击 -> 跑到右缘驻留
cx, cy = pet_rect()
if cx is None: print("FAIL 找不到 BeanPet 窗口"); sys.exit(1)
n0 = len(log_lines())
dblclick(cx, cy)
check("go right edge", wait_for(n0, "go right edge", 10) or wait_for(n0, "pin request", 10))
check("pinned at right edge", wait_for(n0, "pinned at right edge", 15))

# 2) 再双击 -> 解除驻留
cx, cy = pet_rect()
n1 = len(log_lines())
time.sleep(0.6)
dblclick(cx, cy)
check("unpin", wait_for(n1, "unpin", 6))

# 3) 拖拽 -> drag start + dropped at
cx, cy = pet_rect()
n2 = len(log_lines())
abs_move(cx, cy); time.sleep(0.25)
mouse(MOUSEEVENTF_LEFTDOWN); time.sleep(0.12)
for i in range(1, 21):
    abs_move(cx + i * 14, cy + i * 9); time.sleep(0.025)
time.sleep(0.15)
mouse(MOUSEEVENTF_LEFTUP); time.sleep(0.6)
check("drag start", wait_for(n2, "drag start", 4))
check("dropped", wait_for(n2, "dropped at", 4))

print("---- 本轮新增日志 ----")
for ln in log_lines()[n0:]:
    print(ln)
print("RESULT: " + ("ALL PASS" if ok else "HAS FAIL"))
