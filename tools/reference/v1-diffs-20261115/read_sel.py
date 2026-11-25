import sys, os
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
d = app.ActiveDoc
print("active:", d.GetTitle, "| type", d.GetType)
sm = d.SelectionManager
n = sm.GetSelectedObjectCount2(-1)
print("selected:", n)
for i in range(1, n + 1):
    t = sm.GetSelectedObjectType3(i, -1)
    c = sm.GetSelectedObjectsComponent4(i, -1)
    print(" ", i, "type", t, "component", c.Name2 if c else None, os.path.basename(c.GetPathName) if c else "")
if d.GetType == 2:
    ec = d.GetEditTarget
    print("edit target:", ec.GetTitle if ec else None)
