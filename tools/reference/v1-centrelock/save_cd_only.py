r"""Save ONLY v1_CenterDiff_Assem.SLDASM (user-approved) after re-checking mate errors in every configuration and that
the new carrier mates exist and Coincident1 is gone. Refuses if any other open document is dirty. Leaves Default active."""
from lockcommon import *  # noqa: F401,F403
import time
dirty = {p.lower() for p, u in open_docs() if u}
if not dirty <= {CDU.lower()}:
    raise SystemExit(f"STOP: other dirty documents {sorted(dirty - {CDU.lower()})}")
asm = app.GetOpenDocumentByName(CDU)
app.ActivateDoc3(asm.GetTitle, False, 0, out())
ms = mates(asm)
need = ("Carrier at Origin", "Carrier square to Z", "LockDog keyed to Carrier")
if "Coincident1" in ms or not all(n in ms for n in need):
    raise SystemExit("STOP: mates not as expected")
for k in asm.GetConfigurationNames:
    asm.ShowConfiguration2(k); asm.EditRebuild3
    if errors(asm): raise SystemExit(f"STOP: mate errors/warnings in {k}: {errors(asm)}")
asm.ShowConfiguration2("Default"); asm.EditRebuild3
e1, e2 = out(), out()
r = asm.Save3(1, e1, e2)
print(f"Save3 -> {r} | errors {getattr(e1, 'value', e1)} warnings {getattr(e2, 'value', e2)} | GetSaveFlag {bool(asm.GetSaveFlag)}"
      f" | active {asm.ConfigurationManager.ActiveConfiguration.Name}")
print("file modified", time.strftime('%H:%M:%S', time.localtime(os.path.getmtime(CDU))))
for p, u in open_docs():
    if u: print("  still UNSAVED", p)
