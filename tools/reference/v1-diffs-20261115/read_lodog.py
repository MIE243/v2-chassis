import sys, math
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
a = app.GetOpenDocumentByName(r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Transfer Case\v1_TransferCase.SLDASM")
print("config", a.ConfigurationManager.ActiveConfiguration.Name)
for c in a.GetComponents(True) or ():
    if c.Name2 in ("v1_LoDog-1", "v1_TransferCase_Carrier_Carrier-1"):
        d = c.Transform2.ArrayData
        print(c.Name2, "part X axis ->", [round(v, 4) for v in d[0:3]], "angle about Z %.2f deg" % math.degrees(math.atan2(d[1], d[0])),
              "origin", [round(v * 1000, 3) for v in d[9:12]])
