r"""Read-only: v1 Chassis Assembly.SLDASM top-level components/transforms and mates touching a centre diff;
v1_CD_Carrier and v1_CD_Side features/dims/equations/cylinders; master geometry sketch points (model coords).
Opens the master read-only only if not open; closes only what it opened if unmodified. Changes nothing."""
import os, sys, math
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from win32com.client import VARIANT
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
R = r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis"
ch = app.GetOpenDocumentByName(os.path.join(R, "v1 Chassis Assembly.SLDASM"))
print("chassis open:", ch is not None, "unsaved", bool(ch.GetSaveFlag), "config", ch.ConfigurationManager.ActiveConfiguration.Name)
for c in ch.GetComponents(True) or ():
    a = [float(v) for v in c.Transform2.ArrayData]
    print(f"  comp {c.Name2:34} {os.path.basename(c.GetPathName)}\n       rot {[round(v,4) for v in a[:9]]} t {[round(v*M,4) for v in a[9:12]]} fixed={c.IsFixed} supp={c.IsSuppressed}")
f = ch.FirstFeature
while f is not None:
    if f.GetTypeName2 == "MateGroup":
        s = f.GetFirstSubFeature
        while s is not None:
            m = s.GetSpecificFeature2
            ents = []
            try:
                for i in range(m.GetMateEntityCount):
                    e = m.MateEntity(i); c = e.ReferenceComponent
                    ents.append((c.Name2 if c else "asm", e.ReferenceType2))
            except Exception as ex:
                ents = str(ex)
            vals = None
            dd = s.GetFirstDisplayDimension
            if dd is not None:
                vals = round(dd.GetDimension2(0).SystemValue * M, 4)
            try: t = m.Type; fl = m.Flipped
            except Exception: t = fl = "?"
            w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
            code = s.GetErrorCode2(w)
            print(f"  mate {s.Name:30} type {t} flipped {fl} ents {ents} val {vals} supp {s.IsSuppressed} err {code},{w.value}")
            s = s.GetNextSubFeature
    f = f.GetNextFeature


def dump_part(path):
    d = app.GetOpenDocumentByName(path)
    print("=====", os.path.basename(path), "open", d is not None, "unsaved", bool(d.GetSaveFlag) if d else None)
    if d is None: return
    em = d.GetEquationMgr
    for i in range(em.GetCount): print("  eq:", em.Equation(i))
    ff = d.FirstFeature
    while ff is not None:
        dims = []
        dd = ff.GetFirstDisplayDimension
        while dd is not None:
            dm = dd.GetDimension2(0); dims.append((dm.FullName, round(dm.SystemValue * M, 4)))
            dd = ff.GetNextDisplayDimension(dd)
        if ff.GetTypeName2 not in ("MaterialFolder","SensorFolder","DetailCabinet","HistoryFolder","SelectionSetFolder","DocsFolder","CommentsFolder","FavoriteFolder","EqnFolder","InkMarkupFolder","SurfaceBodyFolder","SolidBodyFolder","MarkupCommentFolder","EnvFolder","CameraFolder","AmbientLight","DirectionLight"):
            print(f"  feat {ff.Name:30} {ff.GetTypeName2:22} {dims}")
        ff = ff.GetNextFeature
    cyl = set()
    for bd in d.GetBodies2(0, True) or ():
        bb = [round(v*M,3) for v in bd.GetBodyBox()]
        print("  body box", bb)
        for fc in bd.GetFaces() or ():
            s = fc.GetSurface
            if s.IsCylinder:
                p = list(s.CylinderParams); b = fc.GetBox
                cyl.add((round(p[6]*M*2,3), tuple(round(v,3) for v in p[3:6]), round(p[2]*M,2), round(min(b[2],b[5])*M,2), round(max(b[2],b[5])*M,2)))
    print("  cylinders (dia, axis, origin z, z from, z to):", sorted(cyl))


dump_part(os.path.join(R, "Differentials", "v1_CD_Carrier.SLDPRT"))
dump_part(os.path.join(R, "Differentials", "v1_CD_Side.SLDPRT"))

mp = os.path.join(R, "v1 Chassis Master Geometry.SLDPRT")
md = app.GetOpenDocumentByName(mp); mine = False
if md is None:
    spec = app.GetOpenDocSpec(mp); spec.ReadOnly = True; spec.Silent = True
    md = app.OpenDoc7(spec); mine = True
    print("opened master read-only, error", spec.Error)
print("master unsaved", bool(md.GetSaveFlag))
ff = md.FirstFeature
while ff is not None:
    if ff.GetTypeName2 in ("ProfileFeature", "3DProfileFeature"):
        sk = ff.GetSpecificFeature2
        xf = sk.ModelToSketchTransform.Inverse
        a = [float(v) for v in xf.ArrayData]
        print(f"  sketch {ff.Name}")
        for sp in sk.GetSketchPoints2 or ():
            x, y, z = sp.X, sp.Y, sp.Z
            X = a[0]*x + a[3]*y + a[6]*z + a[9]; Y = a[1]*x + a[4]*y + a[7]*z + a[10]; Z = a[2]*x + a[5]*y + a[8]*z + a[11]
            print(f"     point sketch ({x*M:.3f},{y*M:.3f}) model ({X*M:.3f},{Y*M:.3f},{Z*M:.3f})")
        for sg in sk.GetSketchSegments or ():
            if sg.GetType == 0:
                ln = sg; p0 = ln.GetStartPoint2; p1 = ln.GetEndPoint2
                def mdl(p):
                    x, y, z = p.X, p.Y, p.Z
                    return tuple(round((a[k]*x + a[3+k]*y + a[6+k]*z + a[9+k])*M, 3) for k in range(3))
                print(f"     line {mdl(p0)} -> {mdl(p1)} construction={sg.ConstructionGeometry}")
    ff = ff.GetNextFeature
if mine and not md.GetSaveFlag:
    app.CloseDoc(md.GetTitle); print("closed master")
