import sys, os
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M=1000.0
asm=app.GetOpenDocumentByName(r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\v1 Chassis Assembly.SLDASM")
print("active cfg", asm.ConfigurationManager.ActiveConfiguration.Name)
for c in asm.GetComponents(False) or ():
    a=c.Transform2.ArrayData
    print(f"{c.Name2:50} cfg={c.ReferencedConfiguration:10} supp={c.IsSuppressed} rot={[round(x,2) for x in a[:9]]} t={[round(x*M,2) for x in a[9:12]]} {os.path.basename(c.GetPathName)}")
