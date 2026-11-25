import sys, os
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from win32com.client import VARIANT
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
def err(f):
    w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
    try:
        c = f.GetErrorCode2(w); return c, w.value
    except Exception as e:
        return "?", str(e)
TC = r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Transfer Case"
part = app.GetOpenDocumentByName(os.path.join(TC, "v1_Sprocket_Drive.SLDPRT"))
print("v1_Sprocket_Drive open:", part is not None, "| unsaved:", bool(part.GetSaveFlag) if part else None,
      "| config:", part.ConfigurationManager.ActiveConfiguration.Name if part else None)
f = part.FirstFeature
while f is not None:
    c, w = err(f)
    sup = f.IsSuppressed
    if f.GetTypeName2 not in ("CommentsFolder","FavoriteFolder","HistoryFolder","SelectionSetFolder","SensorFolder","DocsFolder","DetailCabinet","SurfaceBodyFolder","SolidBodyFolder","EnvFolder","InkMarkupFolder","EqnFolder","MaterialFolder"):
        print(f"  {f.Name:22} [{f.GetTypeName2}] error={c} warning={w} suppressed={sup}")
    f = f.GetNextFeature
asm = app.GetOpenDocumentByName(os.path.join(TC, "v1_TransferCase.SLDASM"))
print("v1_TransferCase unsaved:", bool(asm.GetSaveFlag))
f = asm.FirstFeature
while f is not None:
    c, w = err(f)
    if c not in (0, None) or w:
        print(f"  ASSEMBLY {f.Name} [{f.GetTypeName2}] error={c} warning={w}")
    if f.GetTypeName2 == "MateGroup":
        s = f.GetFirstSubFeature
        while s is not None:
            c, w = err(s)
            if c not in (0, None) or w:
                print(f"    MATE {s.Name} error={c} warning={w}")
            s = s.GetNextSubFeature
    f = f.GetNextFeature
for comp in asm.GetComponents(True) or ():
    if comp.Name2.startswith("v1_Sprocket_Drive"):
        print("component", comp.Name2, "config", comp.ReferencedConfiguration, "suppression", comp.GetSuppression2 if hasattr(comp, "GetSuppression2") else "?")
