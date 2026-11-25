r"""Make the centre-diff lock parts as NEW files in Differentials\, copied from app-built Transfer Case parts (sources
unchanged), only globals changed:
  v1_LockDog.SLDPRT    <- Dog_m1.25_N20     Face Width 5, Bore Diameter 14 (unchanged)
  v1_LockHub.SLDPRT    <- Dog_m1.25_N20     Face Width 9, Bore Diameter 8
  v1_LockCollar.SLDPRT <- Sleeve_m1.25_N20  Face Width 10
python.exe make_lockparts.py <src> <pid>"""
import os, sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
from gear_generator.swcom import call, _put_indexed
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
R = r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis"
TC, DF = os.path.join(R, "Transfer Case"), os.path.join(R, "Differentials")
M = 1000.0
out = lambda: swcom._out_long()  # noqa: E731


def vol(doc):
    mp = call(call(doc, "Extension"), "CreateMassProperty")
    mp = mp() if type(mp).__name__ == "method" else mp
    return float(mp.Volume) * 1e9


def box(doc):
    b = [list(x.GetBodyBox()) for x in doc.GetBodies2(0, True) or ()]
    return len(b), [round(v * M, 3) for v in b[0]] if b else None


def get_eq(doc, name):
    em = doc.GetEquationMgr
    for i in range(em.GetCount):
        if em.Equation(i).replace(" ", "").startswith('"' + name.replace(" ", "") + '"='):
            return em.Equation(i)


def set_eq(doc, name, value):
    em = doc.GetEquationMgr
    for i in range(em.GetCount):
        if em.Equation(i).replace(" ", "").startswith('"' + name.replace(" ", "") + '"='):
            _put_indexed(em, "Equation", i, f'"{name}"= {value}')
            doc.ForceRebuild3(False)
            print(f"  {name}: now", em.Equation(i))
            return
    raise SystemExit(f"STOP: no equation {name}")


def cyls(doc):
    c = set()
    for bd in doc.GetBodies2(0, True) or ():
        for fc in bd.GetFaces() or ():
            s = fc.GetSurface
            if s.IsCylinder:
                p = list(s.CylinderParams); bb = fc.GetBox
                c.add((round(p[6] * M * 2, 3), round(min(bb[2], bb[5]) * M, 2), round(max(bb[2], bb[5]) * M, 2)))
    return sorted(c)


JOBS = [("Dog_m1.25_N20.SLDPRT", "v1_LockDog.SLDPRT", {"Face Width": 5}, 5.0),
        ("Dog_m1.25_N20.SLDPRT", "v1_LockHub.SLDPRT", {"Face Width": 9, "Bore Diameter": 8}, 9.0),
        ("Sleeve_m1.25_N20.SLDPRT", "v1_LockCollar.SLDPRT", {"Face Width": 10}, 10.0)]
for src_name, dest_name, globs, fw in JOBS:
    dest = os.path.join(DF, dest_name)
    print("=====", dest_name, "from", src_name)
    if os.path.exists(dest):
        print("  already exists, skipped"); continue
    src = app.GetOpenDocumentByName(os.path.join(TC, src_name))
    if src is None or src.GetSaveFlag:
        raise SystemExit(f"STOP: {src_name} not open, or has unsaved changes")
    print("  source:", get_eq(src, "Face Width"), "|", get_eq(src, "Bore Diameter"), f"| volume {vol(src):.1f} | box", box(src))
    e1, e2 = out(), out()
    call(call(src, "Extension"), "SaveAs3", dest, 0, 1 | 2, swcom._null_dispatch(), swcom._null_dispatch(), e1, e2)
    if not os.path.exists(dest):
        raise SystemExit("STOP: SaveAs3 copy made no file")
    spec = app.GetOpenDocSpec(dest); spec.Silent = True
    doc = app.OpenDoc7(spec)
    print("  opened:", doc is not None, "| source unsaved-free:", not src.GetSaveFlag, "| source path:", src.GetPathName)
    for k, v in globs.items():
        set_eq(doc, k, v)
    n, b = box(doc)
    print(f"  volume {vol(doc):.1f} mm^3 | bodies {n}, box {b}")
    print("  Face Width:", get_eq(doc, "Face Width"), "| Bore:", get_eq(doc, "Bore Diameter"))
    print("  cylinders (dia, z from, z to):", cyls(doc))
    if n != 1 or abs(b[2]) > 1e-3 or abs(b[5] - fw) > 1e-3:
        raise SystemExit(f"STOP: body box is not part Z 0..{fw}; part left unsaved for a look")
    e1, e2 = out(), out(); print("  saved:", doc.Save3(1, e1, e2), "| unsaved after:", bool(doc.GetSaveFlag))
