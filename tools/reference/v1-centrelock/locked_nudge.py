r"""Locked only: try to clear the post-restore mate warnings by moving through the solver instead of Transform2-restoring
everything: push v1_CD_Side-1 by argv[3] deg about world Z (only that component), rebuild, report angles vs
xf_aftermates and mate errors. Ends on Default. Saves nothing."""
from lockcommon import *  # noqa: F401,F403
import json
from dof_helpers import rot_world_z, turned
asm = app.GetOpenDocumentByName(CDU)
app.ActivateDoc3(asm.GetTitle, False, 0, out())
ref = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "xf_aftermates.json")))["cfg"]["Locked"]
deg = float(sys.argv[3]); who = sys.argv[4] if len(sys.argv) > 4 else "v1_CD_Side-1"
asm.ShowConfiguration2("Locked"); asm.EditRebuild3
print("errors before:", "none" if not errors(asm) else f"{len(errors(asm))} mates")
c = comps(asm)[who]; put_xf(c, rot_world_z(xf(c), math.radians(deg))); asm.EditRebuild3
for n, c in sorted(comps(asm).items()):
    print(f"   {n:18} vs baseline: {turned(xf(c), ref[n])}")
e = errors(asm)
print("errors after:", "none" if not e else e)
w = max(max(abs(x - y) for x, y in zip(xf(c), ref[n])) for n, c in comps(asm).items())
print("max diff to baseline", w)
asm.ShowConfiguration2("Default"); asm.EditRebuild3
print("Default errors:", errors(asm) or "none")
