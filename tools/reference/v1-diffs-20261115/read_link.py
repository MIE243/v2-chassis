import sys, os, math
SRC, PID, PATH = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
d = app.GetOpenDocumentByName(PATH); mine = False
if d is None:
    spec = app.GetOpenDocSpec(PATH); spec.ReadOnly = True; spec.Silent = True
    d = app.OpenDoc7(spec); mine = True
print("==", os.path.basename(PATH), "| opened here:", mine, "| configs:", list(d.GetConfigurationNames or ()))
f = d.FirstFeature
while f is not None:
    t = f.GetTypeName2
    if t not in ("CommentsFolder","FavoriteFolder","HistoryFolder","SelectionSetFolder","SensorFolder","DocsFolder","DetailCabinet","SurfaceBodyFolder","SolidBodyFolder","EnvFolder","InkMarkupFolder","EqnFolder","MaterialFolder"):
        extra = ""
        if t == "RefPlane":
            a = f.GetSpecificFeature2.Transform.ArrayData
            extra = f"origin {tuple(round(v*M,3) for v in a[9:12])} normal {tuple(round(v,3) for v in a[6:9])}"
        print(f"  [{t}] {f.Name} {extra}")
    f = f.GetNextFeature
bodies = list(d.GetBodies2(0, True) or ())
for b in bodies:
    bx = list(b.GetBodyBox())
    print("  body box mm:", [round(v*M,3) for v in bx])
    seen = set()
    for face in b.GetFaces() or ():
        s = face.GetSurface
        if s.IsCylinder:
            p = list(s.CylinderParams)  # origin xyz, axis xyz, radius
            key = (tuple(round(v*M,2) for v in p[0:3]), tuple(round(abs(v),3) for v in p[3:6]), round(p[6]*M,3))
            # project origin along axis to remove the arbitrary position along the axis
            ax = p[3:6]; o = p[0:3]
            k = (round(o[0]*M - (o[0]*M*ax[0]+o[1]*M*ax[1]+o[2]*M*ax[2])*ax[0],2), round(o[1]*M - (o[0]*M*ax[0]+o[1]*M*ax[1]+o[2]*M*ax[2])*ax[1],2), round(o[2]*M - (o[0]*M*ax[0]+o[1]*M*ax[1]+o[2]*M*ax[2])*ax[2],2), tuple(round(abs(v),3) for v in ax), round(p[6]*M,3))
            if k not in seen:
                seen.add(k); print("    cylinder: axis through", k[0:3], "dir", k[3], "radius", k[4])
if mine and not d.GetSaveFlag:
    app.CloseDoc(d.GetTitle); print("  (closed again)")
