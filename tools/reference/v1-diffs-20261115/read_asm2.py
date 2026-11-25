r"""Read-only: every top-level component of each open assembly, its origin and its own Z axis in the assembly, and its
box (mm). python.exe read_asm.py <gear-generator src> <pid>"""
import os
import sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom  # noqa: E402
from gear_generator import swcom  # noqa: E402

pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
d = app.GetFirstDocument
while d is not None:
    if d.GetType == 2:
        print("=====", d.GetTitle, "| active config:", d.ConfigurationManager.ActiveConfiguration.Name)
        comps = d.GetComponents(False) or ()
        for c in comps:
            a = c.Transform2.ArrayData
            origin = tuple(round(v * M, 3) for v in a[9:12])
            zaxis = tuple(round(v, 3) for v in a[6:9])
            try:
                box = c.GetBox(False, False)
                zr = (round(box[2] * M, 2), round(box[5] * M, 2))
                xr = (round(box[0] * M, 2), round(box[3] * M, 2))
            except Exception:  # noqa: BLE001
                zr = xr = None
            path = os.path.basename(c.GetPathName or "")
            print(f"  {c.Name2:44} {path:28} origin {origin}  own Z {zaxis}  supp={c.IsSuppressed}")
    d = d.GetNext
