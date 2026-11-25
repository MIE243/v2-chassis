import sys, os
SRC, PID, PATH, MODE = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
d = app.GetOpenDocumentByName(PATH)
print("open:", d is not None, "| unsaved:", bool(d.GetSaveFlag))
def radii():
    out = set()
    for b in d.GetBodies2(0, True) or ():
        for face in b.GetFaces() or ():
            s = face.GetSurface
            if s.IsCylinder:
                out.add(round(list(s.CylinderParams)[6]*M, 3))
    return sorted(out)
print("cylinder radii:", radii(), "| volume", round(d.Extension.CreateMassProperty.Volume*1e9, 2))
f = d.FirstFeature; feats = {}
while f is not None:
    feats[f.Name] = f; f = f.GetNextFeature
bor = feats["BorSke"]
dd = bor.GetFirstDisplayDimension
dims = []
while dd is not None:
    dim = dd.GetDimension2(0)
    dims.append(dim)
    print("  BorSke dimension", dim.FullName, "=", round(dim.SystemValue*M, 4), "mm")
    dd = bor.GetNextDisplayDimension(dd)
print("leftover sketch present:", "Sketch1" in feats)
if MODE == "apply":
    if "Sketch1" in feats:
        d.ClearSelection2(True)
        feats["Sketch1"].Select2(False, 0)
        print("deleted leftover Sketch1:", d.EditDelete())
    target = [x for x in dims if abs(x.SystemValue - 0.3125*0.0254) < 1e-6]
    print("bore dimension(s) at 5/16\":", [x.FullName for x in target])
    for x in target:
        print("  set", x.FullName, "->", x.SetSystemValue3(0.008, 2, None))
    d.EditRebuild3
    print("after: cylinder radii:", radii(), "| volume", round(d.Extension.CreateMassProperty.Volume*1e9, 2))
