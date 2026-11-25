import sys, os
SRC, PID, PATH = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
d = app.GetOpenDocumentByName(PATH)
print("open:", d is not None)
if d is None: raise SystemExit
print("unsaved:", bool(d.GetSaveFlag), "| configs:", list(d.GetConfigurationNames or ()), "| toolbox flag:", d.Extension.ToolboxPartType)
f = d.FirstFeature
while f is not None:
    t = f.GetTypeName2
    if t == "RefPlane":
        a = f.GetSpecificFeature2.Transform.ArrayData
        print(f"  [RefPlane] {f.Name} origin {tuple(round(v*M,3) for v in a[9:12])} normal {tuple(round(v,3) for v in a[6:9])}")
    elif t not in ("CommentsFolder","FavoriteFolder","HistoryFolder","SelectionSetFolder","SensorFolder","DocsFolder","DetailCabinet","SurfaceBodyFolder","SolidBodyFolder","EnvFolder","InkMarkupFolder","EqnFolder","MaterialFolder"):
        print(f"  [{t}] {f.Name}")
    f = f.GetNextFeature
mp = d.Extension.CreateMassProperty
print("volume mm3:", round(mp.Volume * 1e9, 2))
for b in d.GetBodies2(0, True) or ():
    print("body box:", [round(v*M,3) for v in b.GetBodyBox()])
    rs = set()
    for face in b.GetFaces() or ():
        s = face.GetSurface
        if s.IsCylinder:
            p = list(s.CylinderParams)
            rs.add((round(p[6]*M,3), tuple(round(abs(v),3) for v in p[3:6])))
    print("cylinder radii/axes:", sorted(rs)[:8])
