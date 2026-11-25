import sys, os
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
from gear_generator.swcom import call
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
asm=app.GetOpenDocumentByName(r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\v1 Chassis Assembly.SLDASM")
print("active doc:", app.ActiveDoc.GetTitle, "| chassis unsaved", bool(asm.GetSaveFlag))
SH=("v1_InDog","v1_RangeHub","v1_ModeHub","v1_LockHub","v1_Sprocket_Front")
OPTS = (("TreatCoincidenceAsInterference", True), ("TreatSubAssembliesAsComponents", False),
        ("IncludeMultibodyPartInterferences", True), ("MakeInterferingPartsTransparent", False),
        ("CreateFastenersFolder", False), ("IgnoreHiddenBodies", True), ("ShowIgnoredInterferences", False), ("UseTransform", False))
mgr = call(asm, "InterferenceDetectionManager")
for n, v in OPTS: setattr(mgr, n, v)
allr=[]
try:
    items = mgr.GetInterferences
    items = items() if type(items).__name__ == "method" else items
    for it in items or ():
        cn = [str(x.Name2).split("/")[-1] for x in (it.Components or ())]
        allr.append((round(float(it.Volume)*1e9,3), cn))
finally:
    mgr.Done()
print("total interferences", len(allr))
for v,cn in sorted(allr,key=lambda x:-x[0]):
    tag="SHAFT " if any(s in c for c in cn for s in SH) else "      "
    print(tag, v, cn)
