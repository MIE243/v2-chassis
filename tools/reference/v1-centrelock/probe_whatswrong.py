r"""Read-only: What's Wrong list of the chassis and of the transfer case."""
import sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from win32com.client import VARIANT
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
R = r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis"
for p in (R + r"\v1 Chassis Assembly.SLDASM", R + r"\Transfer Case\v1_TransferCase.SLDASM", R + r"\Differentials\v1_CenterDiff_Assem.SLDASM"):
    d = app.GetOpenDocumentByName(p)
    if d is None:
        print("not open:", p); continue
    ext = d.Extension
    n = ext.GetWhatsWrongCount
    print("=====", d.GetTitle, "| what's wrong count:", n, "| unsaved:", bool(d.GetSaveFlag))
    if n:
        feats = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)
        codes = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)
        warns = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)
        ok = ext.GetWhatsWrong(feats, codes, warns)
        fs = feats.value or ()
        for i, f in enumerate(fs):
            try:
                name = f.Name; t = f.GetTypeName2
            except Exception:  # noqa: BLE001
                name, t = "?", "?"
            print(f"   {name:34} {t:18} code {list(codes.value)[i] if codes.value else '?'} warning {list(warns.value)[i] if warns.value else '?'}")
