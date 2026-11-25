import sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
doc=app.GetOpenDocumentByName(r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Transfer Case\v1_Sprocket_Front.SLDPRT")
f=doc.FirstFeature; L=[]
while f is not None: L.append(f"{f.Name}[{f.GetTypeName2}]"); f=f.GetNextFeature
print(L[-8:])
print("bodies",len(list(doc.GetBodies2(0,True))), "cfg", doc.ConfigurationManager.ActiveConfiguration.Name, "configs", list(doc.GetConfigurationNames))
