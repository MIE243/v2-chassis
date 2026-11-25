r"""Read v1 Chassis Master Geometry.SLDPRT read-only on the running SolidWorks and list its reference geometry and
sketches in model coordinates (mm). Opens it read-only and silent; closes it only if this script opened it.
python.exe read_master.py <gear-generator src> <pid> <part path>"""
import sys
SRC, PID, PATH = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sys.path.insert(0, SRC)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom  # noqa: E402
from gear_generator import swcom  # noqa: E402

pythoncom.CoInitialize()
cands = [c for c in swcom.find_candidates() if c.pid == PID]
if not cands:
    print("STOP: SolidWorks", PID, "not reachable"); raise SystemExit(2)
app = cands[0].app
print("attached", cands[0].revision)

M = 1000.0
doc = app.GetOpenDocumentByName(PATH)
opened_here = False
if doc is None:
    spec = app.GetOpenDocSpec(PATH)
    spec.ReadOnly = True
    spec.Silent = True
    doc = app.OpenDoc7(spec)
    opened_here = True
    print("opened read-only; error", spec.Error, "warning", spec.Warning)
else:
    print("already open: reading only, leaving it open")
if doc is None:
    print("STOP: could not open"); raise SystemExit(3)
title = doc.GetTitle
print("title", title, "| units (0=mm):", doc.GetUserPreferenceIntegerValue(0) if False else doc.LengthUnit)


def fmt(p):
    return "(" + ", ".join(f"{v * M:.3f}" for v in p) + ")"


def xf_apply(arr, p):
    # SolidWorks MathTransform ArrayData: 9 rotation (row vectors), 3 translation, 1 scale; p' = p.R*s + t
    r, t, s = arr[0:9], arr[9:12], arr[12]
    return tuple((p[0] * r[0 + j] + p[1] * r[3 + j] + p[2] * r[6 + j]) * s + t[j] for j in range(3))


try:
    feat = doc.FirstFeature
    while feat is not None:
        kind = feat.GetTypeName2
        name = feat.Name
        try:
            sup = feat.IsSuppressed2(1, None)
        except Exception:  # noqa: BLE001
            sup = "?"
        line = f"[{kind}] {name}"
        sf = None
        try:
            sf = feat.GetSpecificFeature2
        except Exception:  # noqa: BLE001
            pass
        if kind == "RefAxis" and sf is not None:
            prm = sf.GetRefAxisParams
            print(line, "from", fmt(prm[0:3]), "to", fmt(prm[3:6]))
        elif kind == "RefPlane" and sf is not None:
            a = sf.Transform.ArrayData
            normal = (a[6], a[7], a[8])
            print(line, "origin", fmt(a[9:12]), "normal", tuple(round(v, 4) for v in normal))
        elif kind in ("RefPoint",) and sf is not None:
            print(line, "at", fmt(sf.GetRefPoint.ArrayData[0:3]))
        elif kind in ("ProfileFeature", "3DProfileFeature") and sf is not None:
            sk = sf
            three = kind == "3DProfileFeature"
            to_model = None if three else sk.ModelToSketchTransform.Inverse.ArrayData
            def P(sp):
                p = (sp.X, sp.Y, sp.Z)
                return p if three else xf_apply(to_model, p)
            print(line, "(3D)" if three else "", "| sketch X axis ->", tuple(round(v, 3) for v in to_model[0:3]) if to_model else "", "sketch Y axis ->", tuple(round(v, 3) for v in to_model[3:6]) if to_model else "")
            segs = sk.GetSketchSegments or ()
            for seg in segs:
                st = seg.GetType  # 0 line, 1 arc, 2 ellipse, 3 spline, 4 text, 5 parabola
                cons = "construction" if seg.ConstructionGeometry else ""
                if st == 0:
                    print("    line", fmt(P(seg.GetStartPoint2)), "->", fmt(P(seg.GetEndPoint2)), cons)
                elif st == 1:
                    print("    arc/circle centre", fmt(P(seg.GetCenterPoint2)), "r", f"{seg.GetRadius * M:.3f}", cons)
                else:
                    print("    segment type", st, cons)
            pts = sk.GetSketchPoints2 or ()
            for sp in pts:
                print("    point model", fmt(P(sp)), " raw sketch", fmt((sp.X, sp.Y, sp.Z)))
        else:
            print(line)
        feat = feat.GetNextFeature
finally:
    if opened_here:
        app.CloseDoc(title)
        print("closed", title)
