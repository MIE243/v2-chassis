r"""Discard the rebuild-only dirty state of v1_CD_Side / v1_CD_Spider (clean at session start; dirtied by step 1's
ForceRebuild3) by reloading them from disk. Their files are not written."""
from lockcommon import *  # noqa: F401,F403
for stem in ("v1_CD_Side", "v1_CD_Spider"):
    d = app.GetOpenDocumentByName(os.path.join(DF, stem + ".SLDPRT"))
    if d is None or not d.GetSaveFlag:
        print(stem, "not dirty / not open"); continue
    em = d.GetEquationMgr; bore = [em.Equation(i) for i in range(em.GetCount) if "Bore" in em.Equation(i)]
    r = d.ReloadOrReplace(False, "", True)
    d = app.GetOpenDocumentByName(os.path.join(DF, stem + ".SLDPRT"))
    print(f"{stem}: ReloadOrReplace -> {r} | unsaved now {bool(d.GetSaveFlag)} | bore eq before {bore}")
asm = app.GetOpenDocumentByName(CDU)
app.ActivateDoc3(asm.GetTitle, False, 0, out()); asm.EditRebuild3
print("errors", errors(asm) or "none")
for p, u in open_docs():
    if u: print("  UNSAVED", p)
