r"""Read-only: anything in error inside v1_TransferCase.SLDASM: its own features/mates, and each part's features."""
import sys, os
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from win32com.client import VARIANT
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
asm = app.GetOpenDocumentByName(r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Transfer Case\v1_TransferCase.SLDASM")
print("TC loaded:", asm is not None, "| unsaved:", bool(asm.GetSaveFlag), "| active cfg:", asm.ConfigurationManager.ActiveConfiguration.Name)
def err(feat):
    w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
    return feat.GetErrorCode2(w), w.value
def walk_feats(doc, label):
    f = doc.FirstFeature
    while f is not None:
        code, warn = err(f)
        if code or warn:
            print(f"  [{label}] FEATURE {f.Name:30} {f.GetTypeName2:18} error {code} warning {warn}")
        if f.GetTypeName2 == "MateGroup":
            s = f.GetFirstSubFeature
            while s is not None:
                code, warn = err(s)
                if code or warn:
                    print(f"  [{label}] MATE {s.Name:30} error {code} warning {warn} suppressed {s.IsSuppressed}")
                s = s.GetNextSubFeature
        sub = f.GetFirstSubFeature if f.GetTypeName2 not in ("MateGroup",) else None
        while sub is not None:
            code, warn = err(sub)
            if code or warn:
                print(f"  [{label}] SUBFEATURE {f.Name}/{sub.Name} {sub.GetTypeName2} error {code} warning {warn}")
            sub = sub.GetNextSubFeature
        f = f.GetNextFeature
walk_feats(asm, "TC")
seen = set()
for c in asm.GetComponents(False) or ():
    p = c.GetPathName or ""
    if p in seen: continue
    seen.add(p)
    d = c.GetModelDoc2
    if d is None:
        print("  no doc:", c.Name2, "| suppressed:", c.IsSuppressed); continue
    walk_feats(d, os.path.basename(p))
print("done")
