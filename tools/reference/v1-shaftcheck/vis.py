import sys, os
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
asm=app.GetOpenDocumentByName(r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\v1 Chassis Assembly.SLDASM")
for c in asm.GetComponents(False) or ():
    n=c.Name2
    if "Chain" in n or "Belt" in n: continue
    print(f"{n:50} vis={c.Visible} supp={c.GetSuppression2} excl={c.ExcludeFromBOM} envelope={c.IsEnvelope} virt={c.IsVirtual}")
