r"""Make the long range sleeve and the range hub as NEW parts in Transfer Case\, copied from the app-built parts so
the tooth form is the app's own. The source parts and the assembly are not changed.
  v1_RangeHub.SLDPRT    <- v1_InDog.SLDPRT,        "Face Width" 5 -> 20 (17T external, bore 8)
  v1_RangeSleeve.SLDPRT <- Sleeve_m1.25_N17.SLDPRT, "Face Width" 10 -> 26, then a Ø26 relief bore cut from part Z 5 to 21
python.exe make_parts.py <src> <pid>"""
import os, sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
from gear_generator.swcom import call, _put_indexed
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
TC = r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Transfer Case"
M = 1000.0
out = lambda: swcom._out_long()  # noqa: E731


def vol(doc):
    mp = call(call(doc, "Extension"), "CreateMassProperty")
    mp = mp() if type(mp).__name__ == "method" else mp
    return float(mp.Volume) * 1e9


def box(doc):
    b = [list(x.GetBodyBox()) for x in doc.GetBodies2(0, True) or ()]
    return len(b), [round(v * M, 3) for v in b[0]] if b else None


def set_eq(doc, name, value):
    em = doc.GetEquationMgr
    for i in range(em.GetCount):
        if em.Equation(i).replace(" ", "").startswith('"' + name.replace(" ", "") + '"='):
            _put_indexed(em, "Equation", i, f'"{name}"= {value}')
            doc.ForceRebuild3(False)
            print(f"  {name}: now", em.Equation(i))
            return
    raise SystemExit(f"STOP: no equation {name}")


def copy(src_name, dest_name):
    src = app.GetOpenDocumentByName(os.path.join(TC, src_name))
    dest = os.path.join(TC, dest_name)
    if os.path.exists(dest):
        doc = app.GetOpenDocumentByName(dest)
        if doc is None or dest_name != "v1_RangeHub.SLDPRT":
            raise SystemExit(f"STOP: {dest_name} already exists")
        print(f"--- {dest_name}: reusing the copy made by the first run (still open, unchanged)")
        return doc
    if src is None or src.GetSaveFlag:
        raise SystemExit(f"STOP: {src_name} not open, or has unsaved changes")
    e1, e2 = out(), out()
    call(call(src, "Extension"), "SaveAs3", dest, 0, 1 | 2, swcom._null_dispatch(), swcom._null_dispatch(), e1, e2)
    spec = app.GetOpenDocSpec(dest); spec.Silent = True
    doc = app.OpenDoc7(spec)
    print(f"--- {dest_name} made from {src_name}; opened:", doc is not None, "| source still unsaved-free:", not src.GetSaveFlag)
    return doc


# Hub
hub = copy("v1_InDog.SLDPRT", "v1_RangeHub.SLDPRT")
v0 = vol(hub); set_eq(hub, "Face Width", 20)
print(f"  volume {v0:.1f} -> {vol(hub):.1f} mm^3 | bodies, box:", box(hub))
e1, e2 = out(), out(); print("  saved:", hub.Save3(1, e1, e2))

# Sleeve
slv = copy("Sleeve_m1.25_N17.SLDPRT", "v1_RangeSleeve.SLDPRT")
v0 = vol(slv); set_eq(slv, "Face Width", 26)
v1 = vol(slv); print(f"  volume {v0:.1f} -> {v1:.1f} mm^3 | bodies, box:", box(slv))
front = None
f = slv.FirstFeature
while f is not None and front is None:
    if f.Name == "Front Plane": front = f
    f = f.GetNextFeature
call(slv, "ClearSelection2", True); front.Select2(False, 0)
plane = call(call(slv, "FeatureManager"), "InsertRefPlane", 8, 0.013, 0, 0.0, 0, 0.0)
a = plane.GetSpecificFeature2.Transform.ArrayData
print("  relief mid plane at part Z", round(a[11] * M, 3), "normal", [round(v, 3) for v in a[6:9]])
if abs(a[11] * M - 13) > 1e-6:
    raise SystemExit("STOP: the plane is not at Z +13; nothing cut, part left unsaved for a look")
plane.Name = "Relief Mid Plane"
call(slv, "ClearSelection2", True); plane.Select2(False, 0)
sm = call(slv, "SketchManager"); sm.InsertSketch(True)
sm.CreateCircleByRadius(0.0, 0.0, 0.0, 0.013); sm.InsertSketch(True)
sk = None
f = slv.FirstFeature
while f is not None:
    if f.GetTypeName2 == "ProfileFeature": sk = f
    f = f.GetNextFeature
sk.Name = "Relief Sketch"
call(slv, "ClearSelection2", True); sk.Select2(False, 0)
cut = call(call(slv, "FeatureManager"), "FeatureCut4", True, False, False, 6, 0, 0.016, 0.0, False, False, False, False,
           0.0, 0.0, False, False, False, False, False, True, True, True, True, False, 0, 0.0, False, False)
call(slv, "ClearSelection2", True)
if cut is None:
    raise SystemExit("STOP: the relief cut made nothing; part left unsaved for a look")
cut.Name = "Relief Bore"
slv.ForceRebuild3(False)
v2 = vol(slv)
print(f"  relief cut: volume {v1:.1f} -> {v2:.1f} mm^3 (removed {v1 - v2:.1f}) | bodies, box:", box(slv))
# probe the bore radius along Z: a point at r 12.5 should be empty in the relief and solid... check by faces
cyl = []
for b in slv.GetBodies2(0, True) or ():
    for fc in b.GetFaces() or ():
        s = fc.GetSurface
        if s.IsCylinder:
            p = list(s.CylinderParams); bb = fc.GetBox
            cyl.append((round(p[6] * M, 3), round(min(bb[2], bb[5]) * M, 2), round(max(bb[2], bb[5]) * M, 2)))
print("  cylindrical faces (r, z from, z to):", sorted(set(cyl)))
e1, e2 = out(), out(); print("  saved:", slv.Save3(1, e1, e2))
