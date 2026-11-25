r"""DOF test, part 2, per configuration:
  C) rigid +10 deg about world Z of EVERY component (the motion a locked diff makes): does the solver keep it?
  D) the 3 bevel gear mates suppressed (this configuration only), carrier alone pushed +10 deg: geometric DOF of the
     case (spiders orbit? lock chain follows in Locked?) without SolidWorks' gear-mate behaviour.
After each: restore every component to its recorded transform; if warnings remain, re-seat the active gear mates
(suppress this config -> put transforms -> unsuppress) as in locked_reset.py. Ends on Default. Saves nothing."""
from lockcommon import *  # noqa: F401,F403
from dof_helpers import rot_world_z, turned
asm = app.GetOpenDocumentByName(CDU)
app.ActivateDoc3(asm.GetTitle, False, 0, out())
CFGS = sys.argv[3].split(",") if len(sys.argv) > 3 else list(asm.GetConfigurationNames)
CAR = "v1_CD_Carrier-1"
BEVEL = ["GearMate1", "GearMate2", "GearMate3"]
GM = BEVEL + ["LockCollar rides LockHub", "LockCollar engages LockDog"]
T = math.radians(10.0)


def rb(): asm.EditRebuild3
def diff(base): return max(max(abs(x - y) for x, y in zip(xf(c), base[n])) for n, c in comps(asm).items())


def report(base):
    for n, c in sorted(comps(asm).items()): print(f"     {n:18} {turned(xf(c), base[n])}")
    print(f"     warnings/errors: {[e[0] for e in errors(asm)] or 'none'}")


def suppress(names, on):
    for n in names: mates(asm)[n].SetSuppression2(0 if on else 2, 1, None)
    rb()


def restore(base, active_gm):
    for n, c in comps(asm).items(): put_xf(c, base[n])
    rb()
    if diff(base) < 1e-9 and not errors(asm): return "transforms"
    suppress(active_gm, True)
    for n, c in comps(asm).items(): put_xf(c, base[n])
    rb(); suppress(active_gm, False)
    return "re-seat" if diff(base) < 1e-9 and not errors(asm) else f"FAILED diff {diff(base):.2e} errors {errors(asm)}"


ok = True
for k in CFGS:
    asm.ShowConfiguration2(k); rb()
    base = {n: xf(c) for n, c in comps(asm).items()}
    active_gm = [n for n in GM if not mates(asm)[n].IsSuppressed2(1, None)[0]]
    print(f"===== [{k}] warnings {len(errors(asm))} | active gear mates {active_gm}")
    for n, c in comps(asm).items(): put_xf(c, rot_world_z(base[n], T))
    rb(); print("  C) everything turned +10 deg, rebuilt ->"); report(base)
    r = restore(base, active_gm); print("  restore:", r); ok &= not r.startswith("FAILED")
    suppress(BEVEL, True)
    put_xf(comps(asm)[CAR], rot_world_z(base[CAR], T)); rb()
    print("  D) bevel gear mates suppressed, carrier pushed +10 deg ->"); report(base)
    for n, c in comps(asm).items(): put_xf(c, base[n])
    rb(); suppress(BEVEL, False)
    r = restore(base, active_gm); print("  restore:", r, "| bevel mates suppressed now", [mates(asm)[n].IsSuppressed2(1, None)[0] for n in BEVEL])
    ok &= not r.startswith("FAILED")
asm.ShowConfiguration2("Default"); rb()
print("active", asm.ConfigurationManager.ActiveConfiguration.Name, "| all restored", ok)
