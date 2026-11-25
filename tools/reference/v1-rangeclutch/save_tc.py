import sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
asm = app.GetOpenDocumentByName(r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Transfer Case\v1_TransferCase.SLDASM")
print("unsaved before:", bool(asm.GetSaveFlag), "| active config:", asm.ConfigurationManager.ActiveConfiguration.Name)
e1, e2 = swcom._out_long(), swcom._out_long()
print("saved:", asm.Save3(1, e1, e2), "| errors", swcom._by_ref(e1) if hasattr(swcom, "_by_ref") else e1, "| unsaved after:", bool(asm.GetSaveFlag))
