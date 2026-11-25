import sys, os
SRC, PID, PATH, MODE = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from win32com.client import VARIANT
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
d = app.GetOpenDocumentByName(PATH)
print(os.path.basename(PATH), "| unsaved:", bool(d.GetSaveFlag))
def err(feat):
    w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
    ole = feat._oleobj_
    r = ole.InvokeTypes(ole.GetIDsOfNames("GetErrorCode2"), 0, pythoncom.DISPATCH_METHOD, (3, 0), ((16395, 3),), w) if False else None
    try:
        r = feat.GetErrorCode2(w)
        return (r, w.value)
    except Exception:
        try:
            return (feat.GetErrorCode, None)
        except Exception as e:
            return ("?", str(e))
bad = []; n = 0
f = d.FirstFeature
while f is not None:
    if f.GetTypeName2 == "MateGroup":
        s = f.GetFirstSubFeature
        while s is not None:
            n += 1
            code, warn = err(s)
            sup = s.IsSuppressed
            if code not in (0, None) or warn:
                bad.append((s.Name, code, warn))
            s = s.GetNextSubFeature
    f = f.GetNextFeature
print("mates read:", n, "| with an error or warning:", bad or "none")
if MODE == "save" and not bad:
    e1, e2 = swcom._out_long(), swcom._out_long()
    print("saved:", d.Save3(1, e1, e2), "| unsaved now:", bool(d.GetSaveFlag))
