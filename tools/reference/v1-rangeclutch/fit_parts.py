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
if asm.GetSaveFlag:
    raise SystemExit("STOP: the assembly has unsaved changes")
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


print("errors before:", errors() or "none")
# 1. replace the sleeve
c = comps()["Sleeve_m1.25_N17-1"]
cfg = c.ReferencedConfiguration
call(asm, "ClearSelection2", True)
c.Select4(False, swcom._null_dispatch(), False)
ok = asm.ReplaceComponents2(os.path.join(TC, "v1_RangeSleeve.SLDPRT"), cfg, False, 0, True)
asm.EditRebuild3
print("replace sleeve:", ok, "| now:", [n for n in comps() if "Range" in n or "Sleeve" in n], "| errors:", errors() or "none")
if "v1_RangeSleeve-1" not in comps():
    raise SystemExit("STOP: replacement did not happen")
# 2. sleeve distance per configuration
dim = mates()["RangeSlv along Rear"].GetFirstDisplayDimension.GetDimension2(0)
for k, v in SLEEVE_D.items():
    dim.SetSystemValue3(v / M, 2, [k])
asm.EditRebuild3
print("RangeSlv along Rear now:", [round(x * M, 3) for x in dim.GetSystemValue3(2, CFGS)])
# 3. the hub, placed with the InDog's rotation at Z -55.5
hubpath = os.path.join(TC, "v1_RangeHub.SLDPRT")
if app.GetOpenDocumentByName(hubpath) is None:
    raise SystemExit("STOP: v1_RangeHub is not open")
hub = call(asm, "AddComponent5", hubpath, 0, "", False, "", 0.0, 0.0, -0.0555)
print("hub inserted:", hub.Name2)
xi = [float(v) for v in comps()["v1_InDog-1"].Transform2.ArrayData]
data = xi[:9] + [0.0, 0.0, -0.0555, 1.0, 0.0, 0.0, 0.0]
util = call(app, "GetMathUtility"); ole = util._oleobj_
raw = ole.Invoke(ole.GetIDsOfNames("CreateTransform"), 0, pythoncom.DISPATCH_METHOD, True, VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, data))
swcom._put(hub, "Transform2", raw if hasattr(raw, "ArrayData") else _dynamic.Dispatch(raw))
asm.EditRebuild3
H = f"v1_RangeHub-1@{TITLE}"
L = f"v1_TransferCase_Layout-1@{TITLE}"
sel(f"Rear Axis@{L}", "AXIS", False); sel(f"Gear Axis@{H}", "AXIS", True)
m1 = add_mate(0, False); m1.Name = "RangeHub on Rear Axis"
sel(f"Front Plane@{H}", "PLANE", False); sel(f"Front Plane@{L}", "PLANE", True)
m2 = add_mate(5, True, 0.0555); m2.Name = "RangeHub along Rear"
asm.EditRebuild3
z = comps()["v1_RangeHub-1"].Transform2.ArrayData[11] * M
print(f"hub origin Z after distance mate: {z:.3f}")
if abs(z + 55.5) > 1e-3:
    raise SystemExit("STOP: hub not at Z -55.5; assembly left unsaved for a look")
S = f"v1_RangeSleeve-1@{TITLE}"
for flip in (False, True):
    sel(f"Gear Axis@{S}", "AXIS", False); sel(f"Gear Axis@{H}", "AXIS", True)
    m3 = add_mate(10, flip)
    d = m3.GetDefinition
    print(f"gear mate flip={flip}: ratio {d.GearRatioNumerator}:{d.GearRatioDenominator} reverse {d.Reverse}")
    if d.Reverse:
        m3.Name = "RangeSlv rides RangeHub"; break
    call(asm, "ClearSelection2", True); m3.Select2(False, 0); asm.EditDelete()
asm.EditRebuild3
print("errors now:", errors() or "none")

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
