r"""Save v1_CD_Carrier.SLDPRT and v1_CenterDiff_Assem.SLDASM (user-approved) after re-checking mate errors in every
configuration. Refuses if any other document than these two and the chassis is dirty. Never saves the chassis."""
from lockcommon import *  # noqa: F401,F403
CAR = os.path.join(DF, "v1_CD_Carrier.SLDPRT")
dirty = {p.lower() for p, u in open_docs() if u}
allowed = {CAR.lower(), CDU.lower(), CHASSIS.lower()}
if not dirty <= allowed:
    raise SystemExit(f"STOP: unexpected dirty documents {sorted(dirty - allowed)}")
asm = app.GetOpenDocumentByName(CDU)
app.ActivateDoc3(asm.GetTitle, False, 0, out())
for k in asm.GetConfigurationNames:
    asm.ShowConfiguration2(k); asm.EditRebuild3
    if errors(asm): raise SystemExit(f"STOP: mate errors in {k}: {errors(asm)}")
asm.ShowConfiguration2("Default"); asm.EditRebuild3
car = app.GetOpenDocumentByName(CAR)
print("D1@LAYOUT", round(car.Parameter("D1@LAYOUT").SystemValue * M, 4))
for d in (car, asm):
    e1, e2 = out(), out()
    r = d.Save3(1, e1, e2)
    print(f"Save3 {os.path.basename(d.GetPathName)} -> {r} | errors {e1.value if hasattr(e1, 'value') else e1}, warnings {e2.value if hasattr(e2, 'value') else e2} | unsaved now {bool(d.GetSaveFlag)}")
print("active config", asm.ConfigurationManager.ActiveConfiguration.Name)
for p, u in open_docs():
    if u: print("  still UNSAVED", p)
for f in ("v1_CD_Carrier.SLDPRT", "v1_CenterDiff_Assem.SLDASM", "v1_CD_SideF.SLDPRT", "v1_CD_Side.SLDPRT", "v1_CD_Spider.SLDPRT",
          "v1_LockDog.SLDPRT", "v1_LockHub.SLDPRT", "v1_LockCollar.SLDPRT"):
    import time
    print(f"  {f:28} modified {time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(os.path.join(DF, f))))}")
