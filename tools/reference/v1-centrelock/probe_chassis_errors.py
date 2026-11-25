r"""Read-only: features and mates in error in v1 Chassis Assembly.SLDASM (top level), plus each top component's state."""
import sys, os
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from win32com.client import VARIANT
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
asm = app.GetOpenDocumentByName(r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\v1 Chassis Assembly.SLDASM")
print("open:", asm is not None, "| unsaved:", bool(asm.GetSaveFlag), "| active doc:", app.ActiveDoc.GetTitle if app.ActiveDoc else None)
def err(feat):
    w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
    code = feat.GetErrorCode2(w)
    return code, w.value
f = asm.FirstFeature
while f is not None:
    code, warn = err(f)
    if code or warn:
        print(f"  FEATURE {f.Name:30} {f.GetTypeName2:18} error {code} warning {warn}")
    if f.GetTypeName2 == "MateGroup":
        s = f.GetFirstSubFeature
        while s is not None:
            code, warn = err(s)
            m = s.GetSpecificFeature2
            ents = []
            try:
                for i in range(m.GetMateEntityCount):
                    e = m.MateEntity(i); rc = e.ReferenceComponent
                    ents.append(f"{rc.Name2 if rc else 'asm'}:{e.ReferenceType2}")
            except Exception:  # noqa: BLE001
                pass
            flag = "  <-- ERROR" if code else ("  <-- warning" if warn else "")
            print(f"  mate {s.Name:30} type {m.Type if m else '?':>2} err {code} warn {warn} sup {s.IsSuppressed} {ents}{flag}")
            s = s.GetNextSubFeature
    f = f.GetNextFeature
for c in asm.GetComponents(True) or ():
    a = c.Transform2.ArrayData if c.Transform2 else None
    print(f"  comp {c.Name2:34} {os.path.basename(c.GetPathName or ''):40} supp={c.IsSuppressed} cfg={c.ReferencedConfiguration} origin={[round(v*1000,2) for v in a[9:12]] if a else None}")
