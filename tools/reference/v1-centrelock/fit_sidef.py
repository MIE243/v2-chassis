r"""Step 2b: in v1_CenterDiff_Assem replace ONLY v1_CD_Side-2 (front side gear) with v1_CD_SideF.SLDPRT, mates re-attached.
Checks transform unchanged, mate entities, errors, interference. Saves nothing."""
from lockcommon import *  # noqa: F401,F403
asm = app.GetOpenDocumentByName(CDU)
app.ActivateDoc3(asm.GetTitle, False, 0, out())
cfgs = list(asm.GetConfigurationNames)
NEW = os.path.join(DF, "v1_CD_SideF.SLDPRT")
cs = comps(asm)
if any(n.startswith("v1_CD_SideF-") for n in cs):
    print("already replaced")
else:
    old = cs["v1_CD_Side-2"]
    x0 = xf(old); print("Side-2 before: origin", origin(old), "rot", [round(v, 5) for v in x0[:9]])
    print("mates before:"); [print("  ", mate_desc(asm, s, cfgs)) for s in mates(asm).values()]
    call(asm, "ClearSelection2", True)
    old.Select4(False, swcom._null_dispatch(), False)
    ok = asm.ReplaceComponents2(NEW, old.ReferencedConfiguration, False, 0, True)
    asm.EditRebuild3
    cs = comps(asm)
    print("ReplaceComponents2 ->", ok, "| components now:", list(cs))
    if "v1_CD_SideF-2" not in cs:
        raise SystemExit("STOP: replacement did not happen")
    new = cs["v1_CD_SideF-2"]; x1 = xf(new)
    print("SideF-1 after: origin", origin(new), "rot", [round(v, 5) for v in x1[:9]],
          "| max transform change", max(abs(a - b) for a, b in zip(x0[:12], x1[:12])))
    print("Side-1 still", os.path.basename(cs["v1_CD_Side-1"].GetPathName))
print("mates after:"); [print("  ", mate_desc(asm, s, cfgs)) for s in mates(asm).values()]
print("errors:", errors(asm) or "none")
print("origins:", {n: origin(c) for n, c in comps(asm).items()})
print("interferences:", interferences(asm) or "none")
n = comps(asm)["v1_CD_SideF-2"]
print("SideF-2:", os.path.basename(n.GetPathName), "origin", origin(n), "rot", [round(v, 5) for v in xf(n)[:9]])
print("CD unsaved", bool(asm.GetSaveFlag))
