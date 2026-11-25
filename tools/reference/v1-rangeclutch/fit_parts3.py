r"""In v1_TransferCase.SLDASM (open, saved): replace Sleeve_m1.25_N17-1 with v1_RangeSleeve.SLDPRT (mates re-attached),
set "RangeSlv along Rear" per configuration (2H/4H 55.5, N 48, 4L 40.5), add v1_RangeHub at Z -55.5 on the Rear Axis
(InDog's tooth phase) with an axis, a distance and a 1:1 gear mate to the sleeve (Reverse as the app's coaxial mates).
Then per configuration: mate errors, sleeve/hub positions, interferences touching the sleeve or hub. Leaves the
assembly UNSAVED, 4H active."""
import os, sys
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
SLEEVE_D = {"2H": 55.5, "4H": 55.5, "N": 48.0, "4L": 40.5}
ext = asm.Extension


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
    sd = None
    ok = ext.SelectByID2(name, kind, 0, 0, 0, append, mark, swcom._null_dispatch(), 0)
    if not ok:
        raise SystemExit(f"STOP: could not select {name}")


def add_mate(kind, flip, dist=0.0):
    before = set(mates())
    st = swcom._out_long()
    r = call(asm, "AddMate5", kind, 2, flip, dist, dist, dist, 1.0, 1.0, 0.0, 0.0, 0.0, False, False, 0, st)
    call(asm, "ClearSelection2", True)
    new = [n for n in mates() if n not in before]
    if len(new) != 1:
        raise SystemExit(f"STOP: AddMate5 type {kind} made {new}")
    return mates()[new[0]]



import math
P17 = 2 * math.pi / 17
def ang(c):
    a = c.Transform2.ArrayData
    return math.atan2(a[1], a[0])
def put_rot(c, theta, z):
    data = [math.cos(theta), math.sin(theta), 0.0, -math.sin(theta), math.cos(theta), 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, z / M, 1.0, 0.0, 0.0, 0.0]
    util = call(app, "GetMathUtility"); ole = util._oleobj_
    raw = ole.Invoke(ole.GetIDsOfNames("CreateTransform"), 0, pythoncom.DISPATCH_METHOD, True, VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, data))
    swcom._put(c, "Transform2", raw if hasattr(raw, "ArrayData") else _dynamic.Dispatch(raw))
asm.ShowConfiguration2("4H"); asm.EditRebuild3
cs = comps()
delta = ang(cs["v1_RangeHub-1"]) - ang(cs["v1_RangeSleeve-1"])
print(f"4H: hub - sleeve = {math.degrees(delta):.3f} deg (aligned there)")
gm = mates()["RangeSlv rides RangeHub"]
for k in ("2H", "N", "4L"):
    asm.ShowConfiguration2(k); asm.EditRebuild3
    cs = comps()
    cur = ang(cs["v1_RangeHub-1"]) - ang(cs["v1_RangeSleeve-1"])
    off = (cur - delta) % P17
    if off > P17 / 2: off -= P17
    print(f"[{k}] hub - sleeve = {math.degrees(cur):.3f} deg; off by {math.degrees(off):.3f} deg (mod one tooth)")
    gm = mates()["RangeSlv rides RangeHub"]
    gm.SetSuppression2(0, 1, None); asm.EditRebuild3
    put_rot(cs["v1_RangeHub-1"], ang(cs["v1_RangeHub-1"]) - off, -55.5); asm.EditRebuild3
    gm = mates()["RangeSlv rides RangeHub"]
    gm.SetSuppression2(2, 1, None); asm.EditRebuild3
    cs = comps()
    cur = ang(cs["v1_RangeHub-1"]) - ang(cs["v1_RangeSleeve-1"])
    off2 = (cur - delta) % P17
    if off2 > P17 / 2: off2 -= P17
    print(f"     now off by {math.degrees(off2):.4f} deg; hub Z {cs['v1_RangeHub-1'].Transform2.ArrayData[11]*M:.3f}; mate suppressed here: {gm.IsSuppressed2(1, None)[0]}")
asm.ShowConfiguration2("4H"); asm.EditRebuild3

# 4. per configuration check
OPTS = (("TreatCoincidenceAsInterference", False), ("TreatSubAssembliesAsComponents", False),
        ("IncludeMultibodyPartInterferences", True), ("MakeInterferingPartsTransparent", False),
        ("CreateFastenersFolder", False), ("IgnoreHiddenBodies", True), ("ShowIgnoredInterferences", False), ("UseTransform", False))
for k in CFGS:
    asm.ShowConfiguration2(k); asm.EditRebuild3
    cs = comps()
    zs = {n: round(cs[n].Transform2.ArrayData[11] * M, 3) for n in ("v1_RangeSleeve-1", "v1_RangeHub-1")}
    mgr = call(asm, "InterferenceDetectionManager")
    for n, v in OPTS: setattr(mgr, n, v)
    hits = []
    try:
        items = mgr.GetInterferences
        items = items() if type(items).__name__ == "method" else items
        for it in items or ():
            cn = [str(x.Name2) for x in (it.Components or ())]
            if any("Range" in x for x in cn):
                hits.append((round(float(it.Volume) * 1e9, 3), cn))
    finally:
        mgr.Done()
    print(f"[{k}] origins {zs} | mate errors {errors() or 'none'} | interferences with sleeve/hub: {hits or 'none'}")
asm.ShowConfiguration2("4H"); asm.EditRebuild3
print("active:", asm.ConfigurationManager.ActiveConfiguration.Name, "| unsaved:", bool(asm.GetSaveFlag))
