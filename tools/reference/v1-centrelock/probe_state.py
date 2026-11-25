r"""Read-only: open docs, v1_CenterDiff_Assem components/mates/configs, carrier features, chassis reference config."""
from lockcommon import *  # noqa: F401,F403
print("open documents:")
for p, u in open_docs(): print(f"   {p}  unsaved={u}")
asm = app.GetOpenDocumentByName(CDU)
if asm is None: raise SystemExit("CD not open")
cfgs = list(asm.GetConfigurationNames)
print("CD unsaved:", bool(asm.GetSaveFlag), "| active", asm.ConfigurationManager.ActiveConfiguration.Name, "| configs", cfgs, "| title", asm.GetTitle)
for n, c in comps(asm).items():
    a = xf(c)
    print(f"  comp {n:24} {os.path.basename(c.GetPathName):26} cfg {c.ReferencedConfiguration} rot {[round(v,4) for v in a[:9]]} t {origin(c)} fixed={c.IsFixed} supp={c.IsSuppressed}")
for n, s in mates(asm).items(): print("  mate", mate_desc(asm, s, cfgs))
car = app.GetOpenDocumentByName(os.path.join(DF, "v1_CD_Carrier.SLDPRT"))
print("carrier open", car is not None, "unsaved", bool(car.GetSaveFlag) if car else None)
ff = car.FirstFeature
while ff is not None:
    dims = []
    dd = ff.GetFirstDisplayDimension
    while dd is not None:
        dm = dd.GetDimension2(0); dims.append((dm.FullName, round(dm.SystemValue * M, 4)))
        dd = ff.GetNextDisplayDimension(dd)
    if ff.GetTypeName2 in ("ProfileFeature", "RefPlane", "RefAxis", "RefPoint", "3DProfileFeature") or dims:
        print(f"  feat {ff.Name:24} {ff.GetTypeName2:18} {dims}")
    if ff.GetTypeName2 == "ProfileFeature":
        sk = ff.GetSpecificFeature2
        a = [float(v) for v in sk.ModelToSketchTransform.Inverse.ArrayData]
        def mdl(p):
            x, y, z = p.X, p.Y, p.Z
            return tuple(round((a[k]*x + a[3+k]*y + a[6+k]*z + a[9+k])*M, 3) for k in range(3))
        for sp in sk.GetSketchPoints2 or (): print("     point", mdl(sp))
        for sg in sk.GetSketchSegments or ():
            if sg.GetType == 0: print("     line", mdl(sg.GetStartPoint2), "->", mdl(sg.GetEndPoint2), "constr", sg.ConstructionGeometry)
    ff = ff.GetNextFeature
ch = app.GetOpenDocumentByName(CHASSIS)
print("chassis open", ch is not None, "unsaved", bool(ch.GetSaveFlag) if ch else None)
if ch:
    for c in ch.GetComponents(True) or ():
        if "Center" in c.Name2 or "Centre" in c.Name2 or "CD" in c.Name2:
            print("  chassis comp", c.Name2, c.GetPathName, "refcfg", c.ReferencedConfiguration, "t", origin(c), "rot", [round(v,4) for v in xf(c)[:9]])
