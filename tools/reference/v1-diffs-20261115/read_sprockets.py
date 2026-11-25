import sys, os, math
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
d = app.GetFirstDocument
while d is not None:
    if d.GetType == 2:
        hits = []
        for c in d.GetComponents(False) or ():
            name, path = c.Name2, (c.GetPathName or "")
            if "procket" in name.lower() or "procket" in path.lower() or "dog_m1.25_n20" in path.lower():
                hits.append(c)
        if hits:
            print("=====", d.GetTitle, "| unsaved:", bool(d.GetSaveFlag), "| config:", d.ConfigurationManager.ActiveConfiguration.Name)
            for c in hits:
                a = c.Transform2.ArrayData
                bx = c.GetBox(False, False)
                lo = [round(v * M, 3) for v in bx[0:3]]; hi = [round(v * M, 3) for v in bx[3:6]]
                ctr = [round((lo[i] + hi[i]) / 2, 3) for i in range(3)]
                print(f"  {c.Name2}  config: {c.ReferencedConfiguration}\n     file: {path if False else c.GetPathName}\n     fixed={bool(c.IsFixed)} part origin {tuple(round(v*M,3) for v in a[9:12])} own Z {tuple(round(v,3) for v in a[6:9])}")
                print(f"     box X {lo[0]}..{hi[0]}  Y {lo[1]}..{hi[1]}  Z {lo[2]}..{hi[2]}   -> box centre ({ctr[0]}, {ctr[1]}, {ctr[2]}), width X {round(hi[0]-lo[0],2)} Y {round(hi[1]-lo[1],2)} Z {round(hi[2]-lo[2],2)}")
    d = d.GetNext
