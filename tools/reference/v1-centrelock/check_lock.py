r"""Step 6 (read-only apart from switching configuration; ends on Default): per configuration mate errors, world origins,
z axes, tooth phases, every interference, box gaps (dog to rear side gear back face, hub to dog), collar span."""
from lockcommon import *  # noqa: F401,F403
asm = app.GetOpenDocumentByName(CDU)
app.ActivateDoc3(asm.GetTitle, False, 0, out())
CFGS = list(asm.GetConfigurationNames)
RS, HUB, DOG, COL = "v1_CD_Side-1", "v1_LockHub-1", "v1_LockDog-1", "v1_LockCollar-1"
print("configs", CFGS)
for n, s in mates(asm).items(): print("  mate", mate_desc(asm, s, CFGS))
for k in CFGS:
    asm.ShowConfiguration2(k); asm.EditRebuild3
    cs = comps(asm)
    print(f"===== [{k}] active {asm.ConfigurationManager.ActiveConfiguration.Name} | mate errors {errors(asm) or 'none'}")
    for n, c in cs.items():
        print(f"   {n:18} origin {origin(c)} z-axis {zaxis(c)} supp {c.IsSuppressed}")
    bx = {n: [v * M for v in cs[n].GetBox(False, False)] for n in (RS, HUB, DOG, COL)}
    for n in (RS, HUB, DOG, COL): print(f"   box Z {n:18} {bx[n][2]:.3f} .. {bx[n][5]:.3f}")
    print(f"   gap dog front -> rear side gear back face: {bx[RS][2] - bx[DOG][5]:.3f} | hub front -> dog rear: {bx[DOG][2] - bx[HUB][5]:.3f}"
          f" | collar {bx[COL][2]:.3f}..{bx[COL][5]:.3f}: on hub {max(0, min(bx[COL][5], bx[HUB][5]) - max(bx[COL][2], bx[HUB][2])):.3f}, on dog {max(0, min(bx[COL][5], bx[DOG][5]) - max(bx[COL][2], bx[DOG][2])):.3f}")
    print(f"   phase collar-hub {math.degrees(wrap(ang(cs[COL]) - ang(cs[HUB]))):.4f} | collar-dog {math.degrees(wrap(ang(cs[COL]) - ang(cs[DOG]))):.4f}"
          f" | hub-rear side X {math.degrees(ang(cs[HUB]) - ang(cs[RS])):.4f}")
    print(f"   interferences (all): {interferences(asm) or 'none'}")
asm.ShowConfiguration2("Default"); asm.EditRebuild3
print("active", asm.ConfigurationManager.ActiveConfiguration.Name, "| CD unsaved", bool(asm.GetSaveFlag))
for p, u in open_docs():
    if u: print("  UNSAVED", p)
