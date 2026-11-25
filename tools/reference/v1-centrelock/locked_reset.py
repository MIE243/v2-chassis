r"""Locked only: clear the solver warnings left by the DOF-test restore by re-seating the gear mates in this
configuration: suppress (this configuration) the 5 gear mates, rebuild, put every component back to xf_aftermates
(Locked) by Transform2, rebuild, unsuppress (this configuration), rebuild. Reports warnings and positions at each
step. Ends on Default. Saves nothing."""
from lockcommon import *  # noqa: F401,F403
import json
asm = app.GetOpenDocumentByName(CDU)
app.ActivateDoc3(asm.GetTitle, False, 0, out())
ref = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "xf_aftermates.json")))["cfg"]["Locked"]
GM = ["GearMate1", "GearMate2", "GearMate3", "LockCollar rides LockHub", "LockCollar engages LockDog"]
CFGS = list(asm.GetConfigurationNames)


def diff(): return max(max(abs(x - y) for x, y in zip(xf(c), ref[n])) for n, c in comps(asm).items())
def state(tag): print(f"{tag}: warnings {len(errors(asm))} {[e[0] for e in errors(asm)][:4]} | max diff to baseline {diff():.2e}")


asm.ShowConfiguration2("Locked"); asm.EditRebuild3
state("start")
for n in GM: mates(asm)[n].SetSuppression2(0, 1, None)
asm.EditRebuild3; state("gear mates suppressed")
for n, c in comps(asm).items(): put_xf(c, ref[n])
asm.EditRebuild3; state("transforms put back")
for n in GM: mates(asm)[n].SetSuppression2(2, 1, None)
asm.EditRebuild3; state("gear mates unsuppressed")
for n in GM: print(f"   {n:28} suppressed per config {list(mates(asm)[n].IsSuppressed2(2, CFGS))}")
asm.ShowConfiguration2("Default"); asm.EditRebuild3
print("Default warnings", errors(asm) or "none")
