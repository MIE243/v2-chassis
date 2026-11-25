r"""Step 4/5: add configurations "Open" and "Locked" (copies of Default, which already has the Open values), then in
Locked: "LockCollar from Tip" 35.75 (this configuration only), dog put in the collar's tooth phase, "LockCollar engages
LockDog" unsuppressed (this configuration only). Then in every configuration: collar-hub phase must be 9 deg mod 18 and
(Locked) collar-dog 9 deg; corrected with the suppress / Transform2 / unsuppress pattern if not. Saves nothing."""
from lockcommon import *  # noqa: F401,F403
asm = app.GetOpenDocumentByName(CDU)
app.ActivateDoc3(asm.GetTitle, False, 0, out())
HUB, DOG, COL = "v1_LockHub-1", "v1_LockDog-1", "v1_LockCollar-1"
HALF = math.radians(9.0)


def rebuild(): asm.EditRebuild3


def show(k):
    asm.ShowConfiguration2(k); rebuild()
    if asm.ConfigurationManager.ActiveConfiguration.Name != k:
        raise SystemExit(f"STOP: could not activate {k}")


show("Default")
for name in ("Open", "Locked"):
    if name in list(asm.GetConfigurationNames):
        print(name, "exists"); continue
    show("Default")
    r = asm.AddConfiguration3(name, "", "", 0)
    print(f"AddConfiguration3({name}) ->", r, "| active now", asm.ConfigurationManager.ActiveConfiguration.Name,
          "| configs", list(asm.GetConfigurationNames))
    if name not in list(asm.GetConfigurationNames):
        raise SystemExit("STOP: configuration not added")
CFGS = list(asm.GetConfigurationNames)
ms = mates(asm)
dim = ms["LockCollar from Tip"].GetFirstDisplayDimension.GetDimension2(0)
eng = "LockCollar engages LockDog"
print("before Locked edits: collar distance", [round(v * M, 3) for v in dim.GetSystemValue3(2, CFGS)],
      "| engage suppressed", list(ms[eng].IsSuppressed2(2, CFGS)))
show("Locked")
if abs(dim.SystemValue * M - 35.75) > 1e-6:
    print("SetSystemValue3 35.75 ->", dim.SetSystemValue3(35.75 / M, 1, None)); rebuild()
if mates(asm)[eng].IsSuppressed2(1, None)[0]:
    cs = comps(asm)
    put_rot(cs[DOG], ang(cs[COL]) - HALF, origin(cs[DOG])[2]); rebuild()
    print("unsuppress engage ->", mates(asm)[eng].SetSuppression2(2, 1, None)); rebuild()
dim = mates(asm)["LockCollar from Tip"].GetFirstDisplayDimension.GetDimension2(0)
print("after: collar distance", [round(v * M, 3) for v in dim.GetSystemValue3(2, CFGS)],
      "| engage suppressed", list(mates(asm)[eng].IsSuppressed2(2, CFGS)), "| configs", CFGS)


def fix(k, comp, ref, mate):
    cs = comps(asm)
    off = wrap(ang(cs[comp]) - ang(cs[ref]) - HALF if comp == COL else ang(cs[comp]) - ang(cs[ref]) + HALF)
    msg = f"[{k}] {comp} vs {ref}: off {math.degrees(off):.4f} deg"
    if abs(math.degrees(off)) > 0.001:
        mates(asm)[mate].SetSuppression2(0, 1, None); rebuild()
        cs = comps(asm); put_rot(cs[comp], ang(cs[comp]) - off, origin(cs[comp])[2]); rebuild()
        mates(asm)[mate].SetSuppression2(2, 1, None); rebuild()
        cs = comps(asm)
        off = wrap(ang(cs[comp]) - ang(cs[ref]) - HALF if comp == COL else ang(cs[comp]) - ang(cs[ref]) + HALF)
        msg += f" -> corrected, now {math.degrees(off):.4f}"
    print(msg)


for k in CFGS:
    show(k)
    fix(k, COL, HUB, "LockCollar rides LockHub")
    if k == "Locked":
        fix(k, DOG, COL, eng)
show("Default")
print("errors:", errors(asm) or "none", "| active", asm.ConfigurationManager.ActiveConfiguration.Name)
