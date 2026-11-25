r"""Rear axle fit check: v1_FinalDrive and v1_AxleDiff in one new assembly, each at its built frame, then the axle
diff turned about the axle so its spider faces the pinion; interference detection in both states.
Makes one new, unsaved assembly and leaves it open; touches no other document.
python.exe fit_check.py <gear-generator src> <pid> <Differentials folder>"""
import os
import sys
import time
SRC, PID, FOLDER = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sys.path.insert(0, SRC)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom  # noqa: E402
from win32com.client import VARIANT  # noqa: E402
from win32com.client import dynamic as _dynamic  # noqa: E402
from gear_generator import swcom  # noqa: E402
from gear_generator.swcom import call  # noqa: E402

pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
APEX = -252.75   # mm, the rear axle cone tip (viewer frame)
OPTIONS = (("TreatCoincidenceAsInterference", False), ("TreatSubAssembliesAsComponents", False),
           ("IncludeMultibodyPartInterferences", True), ("MakeInterferingPartsTransparent", False),
           ("CreateFastenersFolder", False), ("IgnoreHiddenBodies", True), ("ShowIgnoredInterferences", False),
           ("UseTransform", False))


def member(obj, name):
    value = call(obj, name)
    return value() if type(value).__name__ in ("method", "function") else value


def put_frame(asm, comp, columns, at_mm, quiet=False):
    data = list(columns) + [at_mm[0] / M, at_mm[1] / M, at_mm[2] / M, 1.0, 0.0, 0.0, 0.0]
    utility = call(app, "GetMathUtility")
    ole = utility._oleobj_  # noqa: SLF001
    raw = ole.Invoke(ole.GetIDsOfNames("CreateTransform"), 0, pythoncom.DISPATCH_METHOD, True,
                     VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, data))
    xf = raw if hasattr(raw, "ArrayData") else _dynamic.Dispatch(raw)
    swcom._put(comp, "Transform2", xf)  # noqa: SLF001
    call(asm, "EditRebuild3")
    got = [float(v) for v in call(call(comp, "Transform2"), "ArrayData")]
    err = max(abs(got[i] - data[i]) for i in range(12))
    if not quiet:
        print(f"  frame of {call(comp, 'Name2')}: rotation {[round(v, 3) for v in got[:9]]} origin "
              f"{tuple(round(v * M, 3) for v in got[9:12])} (error {err:.2e})")
    return err < 1e-6


def interferences(asm, label, quiet=False):
    found = []
    mgr = call(asm, "InterferenceDetectionManager")
    for name, value in OPTIONS:
        setattr(mgr, name, value)
    try:
        count = int(member(mgr, "GetInterferenceCount"))
        items = list(member(mgr, "GetInterferences") or ())
        if not quiet:
            print(f"--- {label}: {count} interference(s)")
        for it in items:
            vol = float(member(it, "Volume")) * 1e9
            comps = [str(call(c, "Name2")) for c in (member(it, "Components") or ())]
            found.append((vol, tuple(c.split("/")[-1] for c in comps)))
            if not quiet:
                print(f"    {vol:9.3f} mm^3  between  {'  <->  '.join(comps)}")
    finally:
        mgr.Done()
    return found


def touches(found, a, b):
    return any(any(a in c for c in comps) and any(b in c for c in comps) for _, comps in found)


def clearance(asm, comp, rotation, base, step_dir, a, b, label, top=12.0):
    """Slide comp from base along step_dir until a and b first interfere: the gap between them, to 0.05 mm."""
    def hit(d):
        put_frame(asm, comp, rotation, tuple(base[i] + step_dir[i] * d for i in range(3)), quiet=True)
        return touches(interferences(asm, "", quiet=True), a, b)
    if hit(0.0):
        print(f"  {label}: already touching"); return 0.0
    lo, hi = 0.0, top
    if not hit(hi):
        print(f"  {label}: more than {top} mm"); return top
    while hi - lo > 0.05:
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if hit(mid) else (mid, hi)
    print(f"  {label}: {lo:.2f} to {hi:.2f} mm")
    return lo


IDENTITY = (1, 0, 0, 0, 1, 0, 0, 0, 1)
TURN_X_90 = (1, 0, 0, 0, 0, 1, 0, -1, 0)   # columns: local X -> +X, local Y -> +Z, local Z -> -Y

def open_readonly(path):
    doc = app.GetOpenDocumentByName(path)
    if doc is not None:
        return doc, False
    spec = app.GetOpenDocSpec(path)
    spec.ReadOnly = True
    spec.Silent = True
    doc = app.OpenDoc7(spec)
    print("opened read-only", os.path.basename(path), "error", spec.Error, "warning", spec.Warning)
    return doc, True


REUSE = sys.argv[4] if len(sys.argv) > 4 else ""
asm = None
if REUSE:
    d = app.GetFirstDocument
    while d is not None:
        if d.GetTitle == REUSE and d.GetType == 2 and not d.GetPathName and not (d.GetComponents(True) or ()):
            asm = d
        d = d.GetNext
    print("reusing empty", REUSE, "->", asm is not None)
opened = [open_readonly(os.path.join(FOLDER, n)) for n in ("v1_FinalDrive.SLDASM", "v1_AxleDiff.SLDASM")]
if asm is None:
    template = app.GetUserPreferenceStringValue(9)
    asm = app.NewDocument(template, 0, 0, 0)
    print("new assembly", call(asm, "GetTitle"), "from", template)
else:
    errs = swcom._out_long() if hasattr(swcom, "_out_long") else 0  # noqa: SLF001
    app.ActivateDoc3(REUSE, False, 0, errs)
fd = call(asm, "AddComponent5", os.path.join(FOLDER, "v1_FinalDrive.SLDASM"), 0, "", False, "", 0.0, 0.0, 0.0)
ax = call(asm, "AddComponent5", os.path.join(FOLDER, "v1_AxleDiff.SLDASM"), 0, "", False, "", 0.0, 0.0, 0.0)
print("inserted", call(fd, "Name2"), "and", call(ax, "Name2"))
ok = put_frame(asm, fd, IDENTITY, (0, 0, 0)) and put_frame(asm, ax, IDENTITY, (0, 0, 0))
print("frames as built:", ok)
interferences(asm, "as built (spider on +Y, 90 deg from the pinion)")
# p' = R (p - a) + a about the axle line through the cone tip a = (0, 0, APEX): t = a - R a = (0, -APEX... )
ok = put_frame(asm, ax, TURN_X_90, (0.0, APEX, APEX))
print("axle diff turned 90 deg about the axle:", ok)
interferences(asm, "axle diff turned: spider on +Z, facing the pinion")
print("--- room left (slide the diff gears until they first touch):")
clearance(asm, ax, TURN_X_90, (0.0, APEX, APEX), (0, 0, 1), "FD_Pinion", "AX_Spider", "spider back to pinion, along the pinion axis")
clearance(asm, ax, TURN_X_90, (0.0, APEX, APEX), (-1, 0, 0), "FD_Ring", "AX_Spider", "spider to ring teeth, along the axle toward the ring")
clearance(asm, ax, TURN_X_90, (0.0, APEX, APEX), (-1, 0, 0), "FD_Ring", "AX_Side", "side gear to ring teeth, along the axle toward the ring")
put_frame(asm, ax, TURN_X_90, (0.0, APEX, APEX))
OUT = sys.argv[5] if len(sys.argv) > 5 else ""
if OUT:
    e1, e2 = swcom._out_long(), swcom._out_long()  # noqa: SLF001
    call(call(asm, "Extension"), "SaveAs3", OUT, 0, 1, swcom._null_dispatch(), swcom._null_dispatch(), e1, e2)
    print("saved the check assembly to", OUT, "| unsaved now:", bool(asm.GetSaveFlag))
for doc, mine in opened:
    if mine and not doc.GetSaveFlag:
        app.CloseDoc(doc.GetTitle)
        print("closed its window (still loaded in the check assembly):", doc.GetTitle)
print("left open, unsaved:", call(asm, "GetTitle"))
