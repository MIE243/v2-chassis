import sys, win32gui, win32process
pid = int(sys.argv[1])
def each(h, _):
    if win32gui.IsWindowVisible(h) and win32process.GetWindowThreadProcessId(h)[1] == pid:
        kids = []
        win32gui.EnumChildWindows(h, lambda c, k: k.append(win32gui.GetWindowText(c)) or True, kids)
        print(hex(h), win32gui.GetClassName(h), repr(win32gui.GetWindowText(h)), [k for k in kids if k][:10])
    return True
win32gui.EnumWindows(each, None)
