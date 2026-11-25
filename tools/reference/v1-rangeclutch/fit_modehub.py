r"""In v1_TransferCase.SLDASM (open; may carry the user's unsaved range-sleeve edit): add v1_ModeHub at Z -84.5 on the
Rear Axis (dog's tooth phase in 4H), mate it (axis + distance), delete "ModeSlv splined to RangeSlv", add the 1:1 gear mate
"ModeSlv rides ModeHub" (Reverse True), set "ModeSlv along Rear" to 84.5 in 2H only, align the hub's teeth to the sleeve
per configuration, then check each configuration. Leaves the assembly UNSAVED, 4H active.
Re-runnable: steps already done are skipped."""
import math, os, sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from win32com.client import VARIANT
from win32com.client import dynamic as _dynamic
from gear_generator import swcom
from gear_generator.swcom import call
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
TC = r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Transfer Case"
asm = app.GetOpenDocumentByName(os.path.join(TC, "v1_TransferCase.SLDASM"))
TITLE = os.path.splitext(asm.GetTitle)[0]
app.ActivateDoc3(asm.GetTitle, False, 0, swcom._out_long())
CFGS = ["2H", "4H", "N", "4L"]
SLV, HUB, DOG = "Sleeve_m1.25_N20-1", "v1_ModeHub-1", "Dog_m1.25_N20-1"
HUB_Z = -84.5
P20 = 2 * math.pi / 20
ext = asm.Extension
print("assembly unsaved at start:", bool(asm.GetSaveFlag), "| active", asm.ConfigurationManager.ActiveConfiguration.Name)


def comps():
    return {c.Name2: c for c in asm.GetComponents(True) or ()}


def mates():
    out = {}
    f = asm.FirstFeature
    while f is not None:
        if f.GetTypeName2 == "MateGroup":
            s = f.GetFirstSubFeature
            while s is not None:
                out[s.Name] = s
                s = s.GetNextSubFeature
        f = f.GetNextFeature
    return out


def errors():
    bad = []
    for n, s in mates().items():
        w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
        code = s.GetErrorCode2(w)
        if code or w.value:
            bad.append((n, code, w.value))
    return bad


def sel(name, kind, append, mark=1):
    ok = ext.SelectByID2(name, kind, 0, 0, 0, append, mark, swcom._null_dispatch(), 0)
    if not ok:
        raise SystemExit(f"STOP: could not select {name}")


def add_mate(kind, flip, dist=0.0):
    before = set(mates())
    st = swcom._out_long()
    call(asm, "AddMate5", kind, 2, flip, dist, dist, dist, 1.0, 1.0, 0.0, 0.0, 0.0, False, False, 0, st)
    call(asm, "ClearSelection2", True)
    new = [n for n in mates() if n not in before]
    if len(new) != 1:
        raise SystemExit(f"STOP: AddMate5 type {kind} made {new}")
    return mates()[new[0]]


def delete_feat(f):
    call(asm, "ClearSelection2", True); f.Select2(False, 0); asm.EditDelete(); asm.EditRebuild3


def xf(c):
    return [float(v) for v in c.Transform2.ArrayData]


def ang(c):
    a = xf(c)
    return math.atan2(a[1], a[0])


def zaxis(c):
    return [round(v, 6) for v in xf(c)[6:9]]


def put_xf(c, data):
    util = call(app, "GetMathUtility"); ole = util._oleobj_
    raw = ole.Invoke(ole.GetIDsOfNames("CreateTransform"), 0, pythoncom.DISPATCH_METHOD, True,
                     VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, data))
    swcom._put(c, "Transform2", raw if hasattr(raw, "ArrayData") else _dynamic.Dispatch(raw))


def put_rot(c, theta, z):
    put_xf(c, [math.cos(theta), math.sin(theta), 0.0, -math.sin(theta), math.cos(theta), 0.0, 0.0, 0.0, 1.0,
               0.0, 0.0, z / M, 1.0, 0.0, 0.0, 0.0])


def wrap(x):
    x = x % P20
    return x - P20 if x > P20 / 2 else x


def show(k):
    asm.ShowConfiguration2(k); asm.EditRebuild3


print("errors before:", errors() or "none")
H = f"{HUB}@{TITLE}"; L = f"v1_TransferCase_Layout-1@{TITLE}"; S = f"{SLV}@{TITLE}"
show("4H")
cs = comps()
for n in (SLV, DOG):
    a = xf(cs[n]); print(f"4H {n}: origin Z {a[11]*M:.3f}, z axis {zaxis(cs[n])}, angle {math.degrees(ang(cs[n])):.3f} deg")
if zaxis(cs[DOG]) != [0.0, 0.0, 1.0] or zaxis(cs[SLV]) != [0.0, 0.0, 1.0]:
    raise SystemExit("STOP: the dog or the sleeve is not along +Z; angles would need another treatment")
REF = wrap(ang(cs[DOG]) - ang(cs[SLV]))
print(f"aligned reference (dog - sleeve, 4H, mod 18 deg): {math.degrees(REF):.4f} deg")

# 1. insert the hub (4H active) with the dog's rotation
if HUB not in cs:
    hubpath = os.path.join(TC, "v1_ModeHub.SLDPRT")
    if app.GetOpenDocumentByName(hubpath) is None:
        raise SystemExit("STOP: v1_ModeHub is not open")
    hub = call(asm, "AddComponent5", hubpath, 0, "", False, "", 0.0, 0.0, HUB_Z / M)
    print("hub inserted:", hub.Name2)
    if hub.Name2 != HUB:
        raise SystemExit(f"STOP: unexpected component name {hub.Name2}")
    put_xf(hub, xf(cs[DOG])[:9] + [0.0, 0.0, HUB_Z / M, 1.0, 0.0, 0.0, 0.0]); asm.EditRebuild3
    print(f"  hub placed: Z {xf(hub)[11]*M:.3f}, z axis {zaxis(hub)}, angle {math.degrees(ang(hub)):.3f}")
else:
    print("hub already present")

# 2. hub mates
ms = mates()
if "ModeHub on Rear Axis" not in ms:
    sel(f"Rear Axis@{L}", "AXIS", False); sel(f"Gear Axis@{H}", "AXIS", True)
    m1 = add_mate(0, False); m1.Name = "ModeHub on Rear Axis"; asm.EditRebuild3
    print("made ModeHub on Rear Axis")
if "ModeHub along Rear" not in mates():
    for flip in (False, True):
        sel(f"Front Plane@{H}", "PLANE", False); sel(f"Front Plane@{L}", "PLANE", True)
        m2 = add_mate(5, flip, -HUB_Z / M); asm.EditRebuild3
        z = xf(comps()[HUB])[11] * M
        print(f"distance mate flip={flip}: hub origin Z {z:.3f}, z axis {zaxis(comps()[HUB])}")
        if abs(z - HUB_Z) < 1e-3:
            m2.Name = "ModeHub along Rear"; break
        delete_feat(m2)
    else:
        raise SystemExit("STOP: neither flip put the hub at Z -84.5")
c = comps()[HUB]
if zaxis(c) != [0.0, 0.0, 1.0]:
    raise SystemExit("STOP: hub not along +Z after mating")

# 3. re-key the mode sleeve to the hub
ms = mates()
if "ModeSlv splined to RangeSlv" in ms:
    delete_feat(ms["ModeSlv splined to RangeSlv"])
    print("deleted ModeSlv splined to RangeSlv:", "ModeSlv splined to RangeSlv" not in mates())
if "ModeSlv rides ModeHub" not in mates():
    show("4H"); cs = comps()
    # make sure the hub sits in the sleeve's spaces as the dog does before mating
    off = wrap(ang(cs[HUB]) - ang(cs[SLV]) - REF)
    print(f"4H before gear mate: hub off by {math.degrees(off):.4f} deg")
    if abs(off) > 1e-6:
        put_rot(cs[HUB], ang(cs[HUB]) - off, HUB_Z); asm.EditRebuild3
    for flip in (False, True):
        sel(f"Gear Axis@{S}", "AXIS", False); sel(f"Gear Axis@{H}", "AXIS", True)
        m3 = add_mate(10, flip)
        d = m3.GetDefinition
        print(f"gear mate flip={flip}: ratio {d.GearRatioNumerator}:{d.GearRatioDenominator} reverse {d.Reverse}")
        if d.Reverse:
            m3.Name = "ModeSlv rides ModeHub"; break
        delete_feat(m3)
    else:
        raise SystemExit("STOP: no gear mate read Reverse True")
    asm.EditRebuild3
print("errors now:", errors() or "none")

# 4. sleeve 84.5 in 2H only
show("2H")
dim = mates()["ModeSlv along Rear"].GetFirstDisplayDimension.GetDimension2(0)
dim.SetSystemValue3(84.5 / M, 1, None); asm.EditRebuild3
print("ModeSlv along Rear per config:", [round(x * M, 3) for x in dim.GetSystemValue3(2, CFGS)])

# 5. tooth alignment per configuration
for k in CFGS:
    show(k); cs = comps()
    off = wrap(ang(cs[HUB]) - ang(cs[SLV]) - REF)
    msg = f"[{k}] hub off by {math.degrees(off):.4f} deg"
    if abs(math.degrees(off)) > 0.001:
        gm = mates()["ModeSlv rides ModeHub"]
        gm.SetSuppression2(0, 1, None); asm.EditRebuild3
        cs = comps(); put_rot(cs[HUB], ang(cs[HUB]) - off, HUB_Z); asm.EditRebuild3
        gm = mates()["ModeSlv rides ModeHub"]
        gm.SetSuppression2(2, 1, None); asm.EditRebuild3
        cs = comps()
        off2 = wrap(ang(cs[HUB]) - ang(cs[SLV]) - REF)
        msg += f" -> corrected, now {math.degrees(off2):.4f} deg; mate suppressed here: {gm.IsSuppressed2(1, None)[0]}"
    print(msg)

# 6. per configuration check
OPTS = (("TreatCoincidenceAsInterference", False), ("TreatSubAssembliesAsComponents", False),
        ("IncludeMultibodyPartInterferences", True), ("MakeInterferingPartsTransparent", False),
        ("CreateFastenersFolder", False), ("IgnoreHiddenBodies", True), ("ShowIgnoredInterferences", False), ("UseTransform", False))
for k in CFGS:
    show(k); cs = comps()
    zs = {n: round(xf(cs[n])[11] * M, 3) for n in (SLV, HUB, DOG)}
    off = wrap(ang(cs[HUB]) - ang(cs[SLV]) - REF)
    bh, bd, bs = (list(cs[n].GetBox(False, False)) for n in (HUB, DOG, SLV))
    gap = (bh[2] - bd[5]) * M
    gap_o = zs[HUB] - (zs[DOG] + 5.0)  # origins: dog face width 5
    span0 = f"origin-based hub-dog gap {gap_o:.3f}"
    span = f"hub Z {bh[2]*M:.3f}..{bh[5]*M:.3f}, sleeve Z {bs[2]*M:.3f}..{bs[5]*M:.3f}, dog front {bd[5]*M:.3f}"
    mgr = call(asm, "InterferenceDetectionManager")
    for n, v in OPTS: setattr(mgr, n, v)
    hits = []
    try:
        items = mgr.GetInterferences
        items = items() if type(items).__name__ == "method" else items
        for it in items or ():
            cn = [str(x.Name2) for x in (it.Components or ())]
            if any(x in (HUB, SLV) for x in cn):
                hits.append((round(float(it.Volume) * 1e9, 3), cn))
    finally:
        mgr.Done()
    print(f"[{k}] origins {zs} | {span} | box hub-dog gap {gap:.3f}, {span0} | tooth off {math.degrees(off):.4f} deg"
          f"\n     mate errors {errors() or 'none'} | interferences with hub/sleeve: {hits or 'none'}")
show("4H")
print("active:", asm.ConfigurationManager.ActiveConfiguration.Name, "| unsaved:", bool(asm.GetSaveFlag))
