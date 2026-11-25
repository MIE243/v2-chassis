r"""Drag test (as the UI's Rotate Component does): IDragOperator on the carrier, two Drag() calls each given a
rotation of +5 deg about world Z (cumulative -> 5 deg, incremental -> 10 deg), in configuration argv[3] with
TransformType argv[4], DragMode argv[5]. Report, then restore every transform (re-seat gear mates if warnings).
Ends on Default. Saves nothing."""
from lockcommon import *  # noqa: F401,F403
from dof_helpers import turned
asm = app.GetOpenDocumentByName(CDU)
app.ActivateDoc3(asm.GetTitle, False, 0, out())
K, TT, DM = sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
CAR = "v1_CD_Carrier-1"
GM = ["GearMate1", "GearMate2", "GearMate3", "LockCollar rides LockHub", "LockCollar engages LockDog"]


def rb(): asm.EditRebuild3
def diff(base): return max(max(abs(x - y) for x, y in zip(xf(c), base[n])) for n, c in comps(asm).items())


def mk(t):
    util = call(app, "GetMathUtility"); ole = util._oleobj_
    data = [math.cos(t), math.sin(t), 0.0, -math.sin(t), math.cos(t), 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
    raw = ole.Invoke(ole.GetIDsOfNames("CreateTransform"), 0, pythoncom.DISPATCH_METHOD, True,
                     VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, data))
    return raw if hasattr(raw, "ArrayData") else _dynamic.Dispatch(raw)


from lockcommon import _dynamic  # noqa: E402
asm.ShowConfiguration2(K); rb()
base = {n: xf(c) for n, c in comps(asm).items()}
active_gm = [n for n in GM if not mates(asm)[n].IsSuppressed2(1, None)[0]]
print(f"[{K}] warnings {len(errors(asm))} | TransformType {TT} DragMode {DM}")
dop = asm.GetDragOperator
print("AddComponent", dop.AddComponent(comps(asm)[CAR], False))
dop.CollisionDetectionEnabled = False
dop.DynamicClearanceEnabled = False
dop.TransformType = TT
dop.DragMode = DM
print("BeginDrag", dop.BeginDrag)
for i in range(2):
    print(f"  Drag #{i + 1}", dop.Drag(mk(math.radians(5.0))))
print("EndDrag", dop.EndDrag)
rb()
for n, c in sorted(comps(asm).items()): print(f"   {n:18} {turned(xf(c), base[n])}")
print("   warnings/errors:", [e[0] for e in errors(asm)] or "none")
for n, c in comps(asm).items(): put_xf(c, base[n])
rb()
how = "transforms"
if diff(base) > 1e-9 or errors(asm):
    for n in active_gm: mates(asm)[n].SetSuppression2(0, 1, None)
    rb()
    for n, c in comps(asm).items(): put_xf(c, base[n])
    rb()
    for n in active_gm: mates(asm)[n].SetSuppression2(2, 1, None)
    rb(); how = "re-seat"
print(f"restore ({how}): diff {diff(base):.2e} | warnings {len(errors(asm))}")
asm.ShowConfiguration2("Default"); rb()
