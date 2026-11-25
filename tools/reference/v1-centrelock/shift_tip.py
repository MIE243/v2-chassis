r"""Step 1: baseline interference in v1_CenterDiff_Assem, then D1@LAYOUT (v1_CD_Carrier) 151.5 -> 141.5, rebuild part and
assembly, verify sketch points, gear origins, mate errors, interference. Saves nothing."""
from lockcommon import *  # noqa: F401,F403
asm = app.GetOpenDocumentByName(CDU)
car = app.GetOpenDocumentByName(os.path.join(DF, "v1_CD_Carrier.SLDPRT"))
GEARS = ("v1_CD_Side-1", "v1_CD_Side-2", "v1_CD_Spider-1", "v1_CD_Spider-2")


def sketch_pts():
    f = car.FeatureByName("LAYOUT"); sk = f.GetSpecificFeature2
    a = [float(v) for v in sk.ModelToSketchTransform.Inverse.ArrayData]
    pts = []
    for sp in sk.GetSketchPoints2 or ():
        x, y, z = sp.X, sp.Y, sp.Z
        pts.append(tuple(round((a[k]*x + a[3+k]*y + a[6+k]*z + a[9+k])*M, 3) for k in range(3)))
    return pts


app.ActivateDoc3(asm.GetTitle, False, 0, out())
asm.EditRebuild3
print("BEFORE: errors", errors(asm) or "none")
print("  origins", {n: origin(c) for n, c in comps(asm).items() if n in GEARS})
print("  interferences", interferences(asm) or "none")
dim = car.Parameter("D1@LAYOUT")
print("D1@LAYOUT", round(dim.SystemValue * M, 4), "| driven?", dim.DrivenState, "| configs in carrier", list(car.GetConfigurationNames))
print("sketch points before", sketch_pts())
if abs(dim.SystemValue * M - 141.5) > 1e-6:
    r = dim.SetSystemValue3(0.1415, 1, None)
    print("SetSystemValue3 ->", r)
car.ForceRebuild3(False)
print("D1@LAYOUT now", round(dim.SystemValue * M, 4), "| carrier unsaved", bool(car.GetSaveFlag))
print("sketch points after ", sketch_pts())
app.ActivateDoc3(asm.GetTitle, False, 0, out())
asm.ForceRebuild3(False)
print("AFTER: errors", errors(asm) or "none")
cs = comps(asm)
for n in GEARS: print(f"  {n:16} origin {origin(cs[n])} z-axis {zaxis(cs[n])}")
print("  carrier origin", origin(cs["v1_CD_Carrier-1"]))
print("  interferences", interferences(asm) or "none")
print("CD unsaved", bool(asm.GetSaveFlag))
