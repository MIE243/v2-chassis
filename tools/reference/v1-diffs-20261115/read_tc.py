r"""Read-only: components of v1_TransferCase.SLDASM only (if open): name, file, Z extent, suppressed."""
import os, sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
P = r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Transfer Case\v1_TransferCase.SLDASM"
a = app.GetOpenDocumentByName(P)
if a is None:
    print("not open"); raise SystemExit
print("config:", a.ConfigurationManager.ActiveConfiguration.Name)
for c in a.GetComponents(True) or ():
    try:
        b = c.GetBox(False, False); z = f"Z {b[2]*1000:8.2f}..{b[5]*1000:8.2f}  R~{max(abs(b[0]),abs(b[3]),abs(b[1]),abs(b[4]))*1000:6.2f}"
    except Exception:
        z = "(no box)"
    print(f"  {c.Name2:44} {os.path.basename(c.GetPathName or ''):40} {z} supp={c.IsSuppressed}")
