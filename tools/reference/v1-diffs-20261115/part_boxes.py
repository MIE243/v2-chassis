import sys, os
SRC, PID, FOLDER = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
from gear_generator.swcom import call
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
for n in ("v1_FD_Pinion", "v1_FD_Ring", "v1_AX_Side", "v1_AX_Spider", "v1_CD_Side", "v1_CD_Spider"):
    p = os.path.join(FOLDER, n + ".SLDPRT")
    d = app.GetOpenDocumentByName(p)
    if d is None:
        print(n, "not loaded"); continue
    bodies = list(d.GetBodies2(0, True) or ())
    if not bodies:
        print(n, "no solid body"); continue
    boxes = [list(x.GetBodyBox()) for x in bodies]
    b = [min(x[i] for x in boxes) for i in range(3)] + [max(x[i] for x in boxes) for i in range(3, 6)]
    print(n, "solid bodies:", len(bodies))
    lo = [round(v * M, 3) for v in b[0:3]]; hi = [round(v * M, 3) for v in b[3:6]]
    print(f"{n:14} along own axis (Z) from cone tip: {lo[2]} .. {hi[2]}   across: X {lo[0]}..{hi[0]}  Y {lo[1]}..{hi[1]}")
