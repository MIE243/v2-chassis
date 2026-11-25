r"""In v1_TransferCase.SLDASM: replace the broken Concentric1 (sprocket dog <-> drive sprocket's old 1/2" bore) with a
concentric mate between the dog's 14 mm bore and the drive sprocket's new 14 mm bore; check every mate and the
sprockets' positions; save the assembly only if no mate is in error. A dry run ("look") only reports the faces."""
import math
import os
import sys
SRC, PID, MODE = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sys.path.insert(0, SRC)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom  # noqa: E402
from win32com.client import VARIANT  # noqa: E402
from gear_generator import swcom  # noqa: E402
from gear_generator.swcom import call  # noqa: E402

pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
PATH = r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Transfer Case\v1_TransferCase.SLDASM"
asm = app.GetOpenDocumentByName(PATH)
comps = {c.Name2: c for c in (asm.GetComponents(True) or ())}
dog, spr = comps["Dog_m1.25_N20-1"], comps["v1_Sprocket_Drive-1"]


def bore_faces(comp, r_mm):
    found = []
    for b in comp.GetBodies2(0) or ():
        for face in b.GetFaces() or ():
            s = face.GetSurface
            if s.IsCylinder:
                p = list(s.CylinderParams)
                if abs(p[6] * M - r_mm) < 1e-3:
                    found.append((face, tuple(round(v * M, 3) for v in p[0:3]), tuple(round(v, 3) for v in p[3:6])))
    return found


fd, fs = bore_faces(dog, 7.0), bore_faces(spr, 7.0)
print("dog r7 faces:", [(o, a) for _, o, a in fd])
print("drive sprocket r7 faces:", [(o, a) for _, o, a in fs])


def mate_errors():
    bad, names = [], []
    f = asm.FirstFeature
    while f is not None:
        if f.GetTypeName2 == "MateGroup":
            s = f.GetFirstSubFeature
            while s is not None:
                names.append(s.Name)
                w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
                code = s.GetErrorCode2(w)
                if code or w.value:
                    bad.append((s.Name, code, w.value))
                s = s.GetNextSubFeature
        f = f.GetNextFeature
    return bad, names


if MODE != "apply":
    raise SystemExit
if not fd or not fs:
    print("STOP: a 14 mm bore face was not found"); raise SystemExit(2)
errs = swcom._out_long()  # noqa: SLF001
app.ActivateDoc3(asm.GetTitle, False, 0, errs)
before = set(mate_errors()[1])
smgr = asm.SelectionManager
call(asm, "ClearSelection2", True)
for face, _, _ in (fd[0], fs[0]):
    sd = smgr.CreateSelectData
    sd.Mark = 1
    print("  selected face:", face.Select4(True, sd))
result = call(asm, "AddMate5", 1, 2, False, 0.0, 0.0, 0.0, 1, 1, 0.0, 0.0, 0.0, False, False, 0, swcom._out_long())  # noqa: SLF001
call(asm, "ClearSelection2", True)
bad, names = mate_errors()
new = [n for n in names if n not in before]
print("new mate:", new, "| AddMate5 returned", type(result).__name__)
if len(new) != 1:
    print("STOP: no new mate made"); raise SystemExit(3)
old = asm.FeatureByName("Concentric1")
call(asm, "ClearSelection2", True)
old.Select2(False, 0)
print("deleted Concentric1:", asm.EditDelete())
asm.EditRebuild3
bad, names = mate_errors()
print("mates now:", len(names), "| in error:", bad or "none")
for c in asm.GetComponents(True) or ():
    if "Sprocket" in c.Name2:
        bx = c.GetBox(False, False)
        print(f"  {c.Name2}: X {bx[0]*M:.2f}..{bx[3]*M:.2f}  Y {bx[1]*M:.2f}..{bx[4]*M:.2f}  Z {bx[2]*M:.2f}..{bx[5]*M:.2f}")
if not bad:
    e1, e2 = swcom._out_long(), swcom._out_long()  # noqa: SLF001
    print("assembly saved:", asm.Save3(1, e1, e2), "| unsaved now:", bool(asm.GetSaveFlag))
else:
    print("assembly NOT saved")
