import sys, os, time, ctypes
sys.path.insert(0, sys.argv[1])
from gear_generator import swcom
import win32gui, win32ui, win32process, win32con
from PIL import Image
pid, out = int(sys.argv[2]), sys.argv[3]
c = [x for x in swcom.find_candidates() if x.pid == pid][0]
d = swcom.call(c.app, "ActiveDoc")
title, path = str(swcom.call(d, "GetTitle")), str(swcom.call(d, "GetPathName"))
cfg = swcom.call(swcom.call(d, "GetActiveConfiguration"), "Name")
print("active", title, cfg, "modified", bool(swcom.call(d, "GetSaveFlag")))
if swcom.call(d, "GetSaveFlag"):
    ok = swcom.call(swcom.call(d, "Extension"), "SaveAs3", path, 0, 1, swcom._null_dispatch(), swcom._null_dispatch(),
                    swcom._out_long(), swcom._out_long())
    print("saved again", bool(ok), "modified now", bool(swcom.call(d, "GetSaveFlag")))
swcom.call(d, "ViewZoomtofit2")
docs, e = [], swcom.call(c.app, "GetFirstDocument")
while e is not None:
    docs.append((str(swcom.call(e, "GetTitle")), bool(swcom.call(e, "GetSaveFlag"))))
    e = swcom.call(e, "GetNext")
print("documents", docs)
main = []
win32gui.EnumWindows(lambda h, _: main.append(h) if win32gui.IsWindowVisible(h) and win32process.GetWindowThreadProcessId(h)[1] == pid and win32gui.GetWindowText(h).startswith("SOLIDWORKS") else None or True, None)
h = main[0]
print("window", win32gui.GetWindowText(h))
time.sleep(2)
l, t, r, b = win32gui.GetWindowRect(h)
w, hh = r - l, b - t
wdc = win32gui.GetWindowDC(h); dc = win32ui.CreateDCFromHandle(wdc); mem = dc.CreateCompatibleDC()
bmp = win32ui.CreateBitmap(); bmp.CreateCompatibleBitmap(dc, w, hh); mem.SelectObject(bmp)
ctypes.windll.user32.PrintWindow(h, mem.GetSafeHdc(), 2)
i = bmp.GetInfo()
Image.frombuffer("RGB", (i["bmWidth"], i["bmHeight"]), bmp.GetBitmapBits(True), "raw", "BGRX", 0, 1).save(out)
win32gui.DeleteObject(bmp.GetHandle()); mem.DeleteDC(); dc.DeleteDC(); win32gui.ReleaseDC(h, wdc)
print("shot", out, w, hh)
