r"""Read-only: features, equations and dimensions of the InDog and the 17T sleeve, and the transfer case's save state."""
import sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
TC = r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Transfer Case"
asm = app.GetOpenDocumentByName(TC + r"\v1_TransferCase.SLDASM")
print("assembly unsaved changes:", bool(asm.GetSaveFlag), "| config", asm.ConfigurationManager.ActiveConfiguration.Name)
for n in ("v1_InDog.SLDPRT", "Sleeve_m1.25_N17.SLDPRT"):
    d = app.GetOpenDocumentByName(TC + "\\" + n)
    print("=====", n, "open:", d is not None, "| unsaved:", bool(d.GetSaveFlag) if d else None)
    if d is None: continue
    em = d.GetEquationMgr
    for i in range(em.GetCount):
        print("  eq:", em.Equation(i))
    f = d.FirstFeature
    while f is not None:
        t = f.GetTypeName2
        if t not in ("MaterialFolder", "SensorFolder", "DetailCabinet", "HistoryFolder", "SelectionSetFolder", "DocsFolder", "CommentsFolder", "FavoriteFolder", "EqnFolder", "InkMarkupFolder", "SurfaceBodyFolder", "SolidBodyFolder", "OriginProfileFeature", "MarkupCommentFolder", "EnvFolder", "CameraFolder", "AmbientLight", "DirectionLight"):
            dims = []
            dd = f.GetFirstDisplayDimension
            while dd is not None:
                dm = dd.GetDimension2(0)
                dims.append((dm.FullName, round(dm.SystemValue * 1000, 4)))
                dd = f.GetNextDisplayDimension(dd)
            print(f"  {f.Name:28} {t:20} {dims}")
        f = f.GetNextFeature
