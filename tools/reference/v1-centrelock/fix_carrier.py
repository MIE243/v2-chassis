r"""Centre-lock fix, step 1+2 (works in Default; mates apply to all configurations). Re-runnable (skips what exists):
  "Carrier at Origin"        carrier origin point coincident with the assembly origin (must NOT come out as a
                             coordinate-system mate, type 20; else retried with the LAYOUT sketch point at the origin)
  "Carrier square to Z"      carrier Front Plane coincident with the assembly Front Plane
  then Coincident1 (type 20, all 6 DOF) is deleted;
  "LockDog keyed to Carrier" angle mate dog Right Plane / carrier Right Plane at their current angle.
Stops if anything moves. Saves nothing."""
from lockcommon import *  # noqa: F401,F403
import json
asm = app.GetOpenDocumentByName(CDU)
app.ActivateDoc3(asm.GetTitle, False, 0, out())
TITLE = os.path.splitext(asm.GetTitle)[0]
ext = asm.Extension
CAR, DOG = "v1_CD_Carrier-1", "v1_LockDog-1"
asm.ShowConfiguration2("Default"); asm.EditRebuild3
CFGS = list(asm.GetConfigurationNames)
base = {n: xf(c) for n, c in comps(asm).items()}
print("active", asm.ConfigurationManager.ActiveConfiguration.Name, "| errors", errors(asm) or "none")


def rebuild(): asm.EditRebuild3


def sel(name, kind, append):
    if not ext.SelectByID2(name, kind, 0, 0, 0, append, 1, swcom._null_dispatch(), 0):
        raise SystemExit(f"STOP: could not select {name} ({kind})")


def add_mate(kind, align=2, flip=False, angle=0.0):
    before = set(mates(asm))
    st = out()
    r = call(asm, "AddMate5", kind, align, flip, 0.0, 0.0, 0.0, 1.0, 1.0, angle, angle, angle, False, False, 0, st)
    call(asm, "ClearSelection2", True)
    new = [n for n in mates(asm) if n not in before]
    if len(new) != 1:
        raise SystemExit(f"STOP: AddMate5 type {kind} made {new} (returned {r}, status {st})")
    return mates(asm)[new[0]]


def delete_feat(f):
    call(asm, "ClearSelection2", True); f.Select2(False, 0); asm.EditDelete(); rebuild()


def moved(tol=1e-7):
    now = {n: xf(c) for n, c in comps(asm).items()}
    return {n: round(max(abs(a - b) for a, b in zip(now[n], base[n])), 9) for n in base
            if max(abs(a - b) for a, b in zip(now[n], base[n])) > tol}


def mtype(s): return s.GetSpecificFeature2.Type


ms = mates(asm)
if "Carrier at Origin" not in ms:
    sel(f"Point1@Origin@{CAR}@{TITLE}", "EXTSKETCHPOINT", False); sel("Point1@Origin", "EXTSKETCHPOINT", True)
    m = add_mate(0); rebuild()
    print(f"origin-origin coincident -> {m.Name} type {mtype(m)}")
    if mtype(m) == 20:
        delete_feat(m)
        # fall back: the LAYOUT sketch point at the carrier origin
        sk = comps(asm)[CAR].FeatureByName("LAYOUT").GetSpecificFeature2
        a = [float(v) for v in sk.ModelToSketchTransform.Inverse.ArrayData]
        pts = [p for p in sk.GetSketchPoints2 or ()
               if all(abs((a[k] * p.X + a[3 + k] * p.Y + a[6 + k] * p.Z + a[9 + k]) * M) < 1e-6 for k in range(3))]
        print("LAYOUT points at the origin:", len(pts))
        if not pts: raise SystemExit("STOP: no LAYOUT point at the origin")
        call(asm, "ClearSelection2", True)
        sd = asm.SelectionManager.CreateSelectData; sd.Mark = 1
        if not pts[0].Select4(False, sd): raise SystemExit("STOP: LAYOUT point did not select")
        sel("Point1@Origin", "EXTSKETCHPOINT", True)
        m = add_mate(0); rebuild()
        print(f"LAYOUT point - asm origin coincident -> {m.Name} type {mtype(m)}")
        if mtype(m) != 0: raise SystemExit("STOP: still not a plain coincident")
    m.Name = "Carrier at Origin"; rebuild()
    print("  errors", errors(asm) or "none", "| moved", moved() or "nothing")
if "Carrier square to Z" not in mates(asm):
    sel(f"Front Plane@{CAR}@{TITLE}", "PLANE", False); sel("Front Plane", "PLANE", True)
    m = add_mate(0); rebuild()
    print(f"front-front coincident -> {m.Name} type {mtype(m)} align {m.GetSpecificFeature2.Alignment}")
    m.Name = "Carrier square to Z"; rebuild()
    print("  errors", errors(asm) or "none", "| moved", moved() or "nothing")
if errors(asm) or moved(): raise SystemExit("STOP before deleting Coincident1")
if "Coincident1" in mates(asm):
    c1 = mates(asm)["Coincident1"]
    if mtype(c1) != 20: raise SystemExit("STOP: Coincident1 is not the coordinate mate")
    delete_feat(c1)
    print("deleted Coincident1 | errors", errors(asm) or "none", "| moved", moved() or "nothing")
if errors(asm) or moved(): raise SystemExit("STOP after deleting Coincident1")

if "LockDog keyed to Carrier" not in mates(asm):
    cs = comps(asm)
    rel = wrap(ang(cs[DOG]) - ang(cs[CAR]), 2 * math.pi)
    want = abs(rel)
    print(f"dog - carrier angle now {math.degrees(rel):.6f} deg")
    done = False
    for align in (2, 0, 1):
        for flip in (False, True):
            sel(f"Right Plane@{DOG}@{TITLE}", "PLANE", False); sel(f"Right Plane@{CAR}@{TITLE}", "PLANE", True)
            m = add_mate(6, align, flip, want); rebuild()
            cs = comps(asm)
            r2 = wrap(ang(cs[DOG]) - ang(cs[CAR]), 2 * math.pi)
            mv = moved(1e-9)
            print(f"  angle mate align {align} flip {flip}: dog-carrier {math.degrees(r2):.6f} | errors {errors(asm) or 'none'} | moved {mv or 'nothing'}")
            if not mv and not errors(asm):
                m.Name = "LockDog keyed to Carrier"; rebuild(); done = True; break
            delete_feat(m)
            for n, c in comps(asm).items():
                if n in mv: put_xf(c, base[n])
            rebuild()
        if done: break
    if not done: raise SystemExit("STOP: no angle mate kept the dog in place")
for n in ("Carrier at Origin", "Carrier square to Z", "LockDog keyed to Carrier"):
    print("  ", mate_desc(asm, mates(asm)[n], CFGS))
print("final errors", errors(asm) or "none", "| moved", moved() or "nothing", "| mates", list(mates(asm)))
