r"""Step 2a: Differentials\v1_CD_SideF.SLDPRT = copy of v1_CD_Side.SLDPRT (source unchanged), global "Bore Diameter" = 14.
Reports bodies, volume, box, cylinders and the minimum wall from the bore to every non-adjacent face (source too).
Saves the NEW part only if it is one solid. Refuses if the destination exists."""
from lockcommon import *  # noqa: F401,F403
from lockcommon import _put_indexed
import time
SRCP = os.path.join(DF, "v1_CD_Side.SLDPRT"); DEST = os.path.join(DF, "v1_CD_SideF.SLDPRT")


def eqs(doc):
    em = doc.GetEquationMgr
    return [em.Equation(i) for i in range(em.GetCount)]


def set_eq(doc, name, value):
    em = doc.GetEquationMgr
    for i in range(em.GetCount):
        if em.Equation(i).replace(" ", "").startswith('"' + name.replace(" ", "") + '"='):
            r = _put_indexed(em, "Equation", i, f'"{name}"= {value}')
            doc.ForceRebuild3(False)
            print(f"  {name}: now", em.Equation(i), "| put ->", r)
            return
    raise SystemExit(f"STOP: no equation {name}")


def tess(f):
    t = f.GetTessTriangles
    t = t(True) if callable(t) else t
    return [tuple(t[i:i + 3]) for i in range(0, len(t), 3)] if t else []


def analyse(doc, label):
    bodies = list(doc.GetBodies2(0, True) or ())
    print(f"[{label}] bodies {len(bodies)} | volume {vol(doc):.1f} mm^3 | box", [round(v * M, 3) for v in bodies[0].GetBodyBox()])
    faces = list(bodies[0].GetFaces() or ())
    cyl = []
    for f in faces:
        s = f.GetSurface
        if s.IsCylinder:
            p = list(s.CylinderParams); b = f.GetBox
            ax = tuple(round(v, 4) for v in p[3:6]); org = (p[0], p[1])
            cyl.append((round(p[6] * M, 3), ax, round(min(b[2], b[5]) * M, 3), round(max(b[2], b[5]) * M, 3),
                        math.hypot(*org) < 1e-7, f))
    print("  cylinders (r, axis, z from, z to, on axis):", sorted({c[:5] for c in cyl}))
    bores = [c for c in cyl if c[4] and abs(abs(c[1][2]) - 1) < 1e-6]
    rb = min(c[0] for c in bores); bore_faces = [c[5] for c in bores if abs(c[0] - rb) < 1e-6]
    z0 = min(c[2] for c in bores if abs(c[0] - rb) < 1e-6); z1 = max(c[3] for c in bores if abs(c[0] - rb) < 1e-6)
    print(f"  bore r {rb} over part Z {z0}..{z1} ({len(bore_faces)} face(s))")
    adj = set()
    for bf in bore_faces:
        for e in bf.GetEdges or ():
            for af in e.GetTwoAdjacentFaces2 or ():
                if af is not None: adj.add(id(af))  # identity check below via IsSame
    def is_adj(f):
        for bf in bore_faces:
            for e in bf.GetEdges or ():
                for af in e.GetTwoAdjacentFaces2 or ():
                    if af is not None and af.IsSame(f): return True
        return False
    cands = []
    for fi, f in enumerate(faces):
        if any(f.IsSame(bf) for bf in bore_faces) or is_adj(f):
            continue
        for p in set(tess(f)):
            x, y, zz = (v * M for v in p); r = math.hypot(x, y)
            dz = 0.0 if z0 <= zz <= z1 else min(abs(zz - z0), abs(zz - z1))
            cands.append((math.hypot(r - rb, dz), fi, p, r, zz))
    cands.sort()
    best = None
    for est, fi, p, r, zz in cands[:300]:
        for bf in bore_faces:
            got = bf.GetClosestPointOn(*p)
            if got is None: continue
            d = math.dist([v * M for v in p], [v * M for v in got[:3]])
            if best is None or d < best[0]:
                best = (d, fi, r, zz, faces[fi].GetSurface.Identity)
    print(f"  min wall bore -> other faces: {best[0]:.3f} mm at r {best[2]:.3f}, part Z {best[3]:.3f} "
          f"(face #{best[1]}, surface type {best[4]}); faces checked {len(faces) - len(bore_faces)} minus adjacent")
    # radial wall in the bore's Z range: smallest radius of non-adjacent faces whose points fall inside z0..z1
    inside = [c for c in cands if z0 <= c[4] <= z1]
    if inside:
        m = min(inside, key=lambda c: c[3])
        print(f"  smallest radius of a non-adjacent face point within the bore's Z range: r {m[3]:.3f} at Z {m[4]:.3f} -> radial wall {m[3]-rb:.3f}")
    return len(bodies)


src = app.GetOpenDocumentByName(SRCP)
if src is None:
    raise SystemExit("STOP: v1_CD_Side not open")
print("source unsaved flag (from the step-1 assembly rebuild, content unchanged):", bool(src.GetSaveFlag))
if not any(e.replace(" ", "") == '"BoreDiameter"=8' for e in eqs(src)):
    raise SystemExit("STOP: source Bore Diameter is not 8")
print("source equations:", eqs(src))
if not os.path.exists(DEST): analyse(src, "v1_CD_Side (source, read-only)")
doc = None
if os.path.exists(DEST):
    # resume only the copy this script made minutes ago (open, Bore still 8, unmodified); anything else: refuse
    doc = app.GetOpenDocumentByName(DEST)
    age = time.time() - os.path.getmtime(DEST)
    if doc is None or doc.GetSaveFlag or age > 3600 or not any(e.replace(" ", "") == '"BoreDiameter"=8' for e in eqs(doc)):
        raise SystemExit("STOP: v1_CD_SideF.SLDPRT already exists - refusing")
    print(f"resuming the copy made {age:.0f} s ago by this script")
else:
    e1, e2 = out(), out()
    call(call(src, "Extension"), "SaveAs3", DEST, 0, 1 | 2, swcom._null_dispatch(), swcom._null_dispatch(), e1, e2)
    if not os.path.exists(DEST):
        raise SystemExit("STOP: SaveAs3 copy made no file")
    spec = app.GetOpenDocSpec(DEST); spec.Silent = True
    doc = app.OpenDoc7(spec)
print("opened copy:", doc.GetPathName, "| source path still", src.GetPathName, "| source unsaved", bool(src.GetSaveFlag))
set_eq(doc, "Bore Diameter", 14)
print("equations now:", eqs(doc))
n = analyse(doc, "v1_CD_SideF")
if n != 1:
    raise SystemExit("STOP: not one solid body; left unsaved")
e1, e2 = out(), out(); print("saved:", doc.Save3(1, e1, e2), "| unsaved after:", bool(doc.GetSaveFlag))
