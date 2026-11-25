import sys, os
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from win32com.client import VARIANT
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
def err(f):
    w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
    c = f.GetErrorCode2(w); return c, w.value
TC = r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Transfer Case"
part = app.GetOpenDocumentByName(os.path.join(TC, "v1_Sprocket_Drive.SLDPRT"))
asm = app.GetOpenDocumentByName(os.path.join(TC, "v1_TransferCase.SLDASM"))
asm_dirty_before = bool(asm.GetSaveFlag)
e = swcom._out_long()
app.ActivateDoc3(part.GetTitle, False, 0, e)
mr = part.FeatureByName("MateReference")
print("MateReference found:", mr is not None, "| error before:", err(mr))
part.ClearSelection2(True)
print("selected:", mr.Select2(False, 0))
print("deleted:", part.EditDelete())
part.EditRebuild3
left = []
f = part.FirstFeature
while f is not None:
    c, w = err(f)
    if c or w: left.append((f.Name, c, w))
    f = f.GetNextFeature
print("part features still in error:", left or "none")
if not left:
    e1, e2 = swcom._out_long(), swcom._out_long()
    print("part saved:", part.Save3(1, e1, e2))
app.ActivateDoc3(asm.GetTitle, False, 0, e)
asm.EditRebuild3
bad = []
f = asm.FirstFeature
while f is not None:
    c, w = err(f)
    if c or w: bad.append((f.Name, c, w))
    if f.GetTypeName2 == "MateGroup":
        s = f.GetFirstSubFeature
        while s is not None:
            c, w = err(s)
            if c or w: bad.append((s.Name, c, w))
            s = s.GetNextSubFeature
    f = f.GetNextFeature
print("v1_TransferCase features/mates in error now:", bad or "none", "| unsaved:", bool(asm.GetSaveFlag))
if not bad and asm.GetSaveFlag and not asm_dirty_before:
    e1, e2 = swcom._out_long(), swcom._out_long()
    print("assembly saved:", asm.Save3(1, e1, e2))
