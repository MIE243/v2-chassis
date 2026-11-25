r"""Make the mode hub as a NEW part in Transfer Case\, copied from the app-built sprocket dog so the tooth form is the app's own.
  v1_ModeHub.SLDPRT <- Dog_m1.25_N20.SLDPRT, "Face Width" 5 -> 9 (20T external, bore 14)
The source part and the assembly are not changed.
python.exe make_modehub.py <src> <pid>"""
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


def eqs(doc):
    em = doc.GetEquationMgr
    return [em.Equation(i) for i in range(em.GetCount)]


def set_eq(doc, name, value):
    em = doc.GetEquationMgr
    for i in range(em.GetCount):
        if em.Equation(i).replace(" ", "").startswith('"' + name.replace(" ", "") + '"='):
            _put_indexed(em, "Equation", i, f'"{name}"= {value}')
            doc.ForceRebuild3(False)
            print(f"  {name}: now", em.Equation(i))
            return
    raise SystemExit(f"STOP: no equation {name}")


src_name, dest_name = "Dog_m1.25_N20.SLDPRT", "v1_ModeHub.SLDPRT"
dest = os.path.join(TC, dest_name)
if os.path.exists(dest):
    raise SystemExit(f"STOP: {dest_name} already exists")
src = app.GetOpenDocumentByName(os.path.join(TC, src_name))
if src is None or src.GetSaveFlag:
    raise SystemExit(f"STOP: {src_name} not open, or has unsaved changes")
print("source equations:", eqs(src))
print(f"source volume {vol(src):.1f} mm^3 | bodies, box:", box(src))
e1, e2 = out(), out()
call(call(src, "Extension"), "SaveAs3", dest, 0, 1 | 2, swcom._null_dispatch(), swcom._null_dispatch(), e1, e2)
if not os.path.exists(dest):
    raise SystemExit("STOP: SaveAs3 copy made no file")
spec = app.GetOpenDocSpec(dest); spec.Silent = True
hub = app.OpenDoc7(spec)
print(f"--- {dest_name} made from {src_name}; opened:", hub is not None, "| source still unsaved-free:", not src.GetSaveFlag,
      "| source path:", src.GetPathName)
v0 = vol(hub); set_eq(hub, "Face Width", 9)
n, b = box(hub)
print(f"  volume {v0:.1f} -> {vol(hub):.1f} mm^3 | bodies {n}, box {b}")
print("  equations now:", eqs(hub))
if n != 1 or abs(b[2]) > 1e-3 or abs(b[5] - 9) > 1e-3:
    raise SystemExit("STOP: body box is not part Z 0..9; part left unsaved for a look")
cyl = []
for bd in hub.GetBodies2(0, True) or ():
    for fc in bd.GetFaces() or ():
        s = fc.GetSurface
        if s.IsCylinder:
            p = list(s.CylinderParams); bb = fc.GetBox
            cyl.append((round(p[6] * M, 3), round(min(bb[2], bb[5]) * M, 2), round(max(bb[2], bb[5]) * M, 2)))
print("  cylindrical faces (r, z from, z to):", sorted(set(cyl)))
e1, e2 = out(), out(); print("  saved:", hub.Save3(1, e1, e2), "| unsaved after:", bool(hub.GetSaveFlag))
