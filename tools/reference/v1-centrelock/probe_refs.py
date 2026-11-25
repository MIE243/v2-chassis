r"""Read-only: reference features, equations, body boxes of the lock parts and v1_CD_Side."""
from lockcommon import *  # noqa: F401,F403
for stem in ("v1_CD_Side", "v1_LockDog", "v1_LockHub", "v1_LockCollar"):
    d = app.GetOpenDocumentByName(os.path.join(DF, stem + ".SLDPRT"))
    print("==", stem, "open", d is not None, "unsaved", bool(d.GetSaveFlag) if d else None)
    if d is None: continue
    em = d.GetEquationMgr
    print("  eqs:", [em.Equation(i) for i in range(em.GetCount)])
    ff = d.FirstFeature; refs = []
    while ff is not None:
        if ff.GetTypeName2 in ("RefAxis", "RefPlane", "RefPoint", "OriginProfileFeature"): refs.append(ff.Name)
        ff = ff.GetNextFeature
    print("  refs:", refs)
    for b in d.GetBodies2(0, True) or (): print("  box", [round(v * M, 3) for v in b.GetBodyBox()])
    try:
        ax = d.FeatureByName("Gear Axis").GetSpecificFeature2
        ent = ax.GetRefAxisParams; print("  Gear Axis params", [round(v * M, 3) for v in ent])
    except Exception as ex: print("  gear axis read:", ex)
