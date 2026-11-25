r"""Step 3: in v1_CenterDiff_Assem (active config, Default = Open values) insert v1_LockHub / v1_LockDog / v1_LockCollar,
part +Z = world +Z on the main axis, referenced to the rear side gear v1_CD_Side-1 (origin = cone tip):
  hub   : placed at Z -182.25, then Lock mate to v1_CD_Side-1                        ("LockHub locked to RearSide")
  dog   : Gear Axis coincident Side-1 Gear Axis, Front Plane distance 30.75          ("LockDog on Axis", "LockDog from Tip")
  collar: Gear Axis coincident, Front Plane distance 41.75 (Open)                    ("LockCollar on Axis", "LockCollar from Tip")
          tooth phase checked by interference (negative control at 0 deg), then gear mates
          "LockCollar rides LockHub" and "LockCollar engages LockDog" (the latter suppressed in this configuration).
Re-runnable (skips what exists). Saves nothing."""
from lockcommon import *  # noqa: F401,F403
asm = app.GetOpenDocumentByName(CDU)
app.ActivateDoc3(asm.GetTitle, False, 0, out())
TITLE = os.path.splitext(asm.GetTitle)[0]
ext = asm.Extension
RS = "v1_CD_Side-1"; HUB, DOG, COL = "v1_LockHub-1", "v1_LockDog-1", "v1_LockCollar-1"
TIP = origin(comps(asm)[RS])[2]
print("active config", asm.ConfigurationManager.ActiveConfiguration.Name, "| tip Z", TIP, "| errors", errors(asm) or "none")
D_DOG, D_HUB, D_COL = 30.75, 40.75, 41.75
HALF = math.radians(9.0)


def sel(name, kind, append):
    if not ext.SelectByID2(name, kind, 0, 0, 0, append, 1, swcom._null_dispatch(), 0):
        raise SystemExit(f"STOP: could not select {name}")


def add_mate(kind, flip, dist=0.0):
    before = set(mates(asm))
    st = out()
    call(asm, "AddMate5", kind, 2, flip, dist, dist, dist, 1.0, 1.0, 0.0, 0.0, 0.0, False, False, 0, st)
    call(asm, "ClearSelection2", True)
    new = [n for n in mates(asm) if n not in before]
    if len(new) != 1:
        raise SystemExit(f"STOP: AddMate5 type {kind} made {new}")
    return mates(asm)[new[0]]


def delete_feat(f):
    call(asm, "ClearSelection2", True); f.Select2(False, 0); asm.EditDelete(); asm.EditRebuild3


def rebuild():
    asm.EditRebuild3


def insert(stem, z, theta):
    name = stem + "-1"
    if name in comps(asm):
        print(name, "already present"); return comps(asm)[name]
    path = os.path.join(DF, stem + ".SLDPRT")
    if app.GetOpenDocumentByName(path) is None:
        raise SystemExit(f"STOP: {stem} is not open")
    c = call(asm, "AddComponent5", path, 0, "", False, "", 0.0, 0.0, z / M)
    if c.Name2 != name:
        raise SystemExit(f"STOP: inserted as {c.Name2}")
    put_rot(c, theta, z); rebuild()
    print(f"inserted {name}: origin {origin(c)} z-axis {zaxis(c)} angle {math.degrees(ang(c)):.3f}")
    return c


def axis_and_distance(comp, dist, axis_name, dist_name):
    full = f"{comp}@{TITLE}"
    if axis_name not in mates(asm):
        sel(f"Gear Axis@{RS}@{TITLE}", "AXIS", False); sel(f"Gear Axis@{full}", "AXIS", True)
        m = add_mate(0, False); m.Name = axis_name; rebuild()
        print(f"  {axis_name}: z-axis {zaxis(comps(asm)[comp])}, origin {origin(comps(asm)[comp])}")
    if dist_name not in mates(asm):
        want = TIP - dist
        for flip in (False, True):
            sel(f"Front Plane@{full}", "PLANE", False); sel(f"Front Plane@{RS}@{TITLE}", "PLANE", True)
            m = add_mate(5, flip, dist / M); rebuild()
            c = comps(asm)[comp]
            print(f"  distance flip={flip}: origin {origin(c)} z-axis {zaxis(c)}")
            if abs(origin(c)[2] - want) < 1e-3 and zaxis(c) == [0.0, 0.0, 1.0]:
                m.Name = dist_name; break
            delete_feat(m)
        else:
            raise SystemExit(f"STOP: no flip put {comp} at Z {want}")
    c = comps(asm)[comp]
    if zaxis(c) != [0.0, 0.0, 1.0]:
        raise SystemExit(f"STOP: {comp} not along +Z")


def gear_mate(a, b, name):
    if name in mates(asm): return mates(asm)[name]
    for flip in (False, True):
        sel(f"Gear Axis@{a}@{TITLE}", "AXIS", False); sel(f"Gear Axis@{b}@{TITLE}", "AXIS", True)
        m = add_mate(10, flip)
        d = m.GetDefinition
        print(f"  {name} flip={flip}: ratio {d.GearRatioNumerator}:{d.GearRatioDenominator} reverse {d.Reverse}")
        if d.Reverse:
            m.Name = name; rebuild(); return m
        delete_feat(m)
    raise SystemExit(f"STOP: no gear mate {name} read Reverse True")


def col_hits(names):
    return [h for h in interferences(asm) if any(n in h[1] for n in names)]


# --- hub: replace any Lock mate (it failed the rigidity test) by axis + distance + Right Plane key to Side-1
if "LockHub locked to RearSide" in mates(asm):
    delete_feat(mates(asm)["LockHub locked to RearSide"]); print("deleted LockHub locked to RearSide")
th_rs = ang(comps(asm)[RS])   # Side-1 part X in world (its Right Plane normal)
hub = insert("v1_LockHub", TIP - D_HUB, th_rs)
if "LockHub on Axis" not in mates(asm):
    put_rot(comps(asm)[HUB], th_rs, TIP - D_HUB); rebuild()
axis_and_distance(HUB, D_HUB, "LockHub on Axis", "LockHub from Tip")
if "LockHub keyed to RearSide" not in mates(asm):
    sel(f"Right Plane@{HUB}@{TITLE}", "PLANE", False); sel(f"Right Plane@{RS}@{TITLE}", "PLANE", True)
    m = add_mate(0, False); m.Name = "LockHub keyed to RearSide"; rebuild()
hub = comps(asm)[HUB]
print(f"hub: origin {origin(hub)} z-axis {zaxis(hub)} angle {math.degrees(ang(hub)):.3f} (side-1 X angle {math.degrees(ang(comps(asm)[RS])):.3f}) | errors {errors(asm) or 'none'}")
if abs(origin(hub)[2] - (TIP - D_HUB)) > 1e-3 or zaxis(hub) != [0.0, 0.0, 1.0]:
    raise SystemExit("STOP: hub misplaced")

# rigidity test: try to rotate and slide the hub; it must keep its pose relative to the rear side gear
def rel_pose():
    h, s = xf(comps(asm)[HUB]), xf(comps(asm)[RS])
    # hub origin and hub X axis expressed in Side-1 frame
    Rs = [s[0:3], s[3:6], s[6:9]]; d = [h[9 + k] - s[9 + k] for k in range(3)]
    o = [sum(Rs[i][k] * d[k] for k in range(3)) * M for i in range(3)]
    xa = [sum(Rs[i][k] * h[k] for k in range(3)) for i in range(3)]
    return [round(v, 4) for v in o], [round(v, 5) for v in xa]
p0 = rel_pose()
h = comps(asm)[HUB]; th0 = ang(h)
put_rot(h, th0 + math.radians(5), origin(h)[2] - 3.0); rebuild()
p1 = rel_pose()
print(f"rigidity test (hub pushed 5 deg / 3 mm): relative pose before {p0} after {p1} -> {'HELD' if p0 == p1 else 'CHANGED'}"
      f"; hub origin now {origin(comps(asm)[HUB])}, side-1 origin {origin(comps(asm)[RS])}")
if p0 != p1 or abs(origin(comps(asm)[HUB])[2] - (TIP - D_HUB)) > 1e-3:
    raise SystemExit("STOP: hub not rigid to the rear side gear")

# --- dog (free to turn; start in the hub's phase)
dog = insert("v1_LockDog", TIP - D_DOG, ang(comps(asm)[HUB]))
axis_and_distance(DOG, D_DOG, "LockDog on Axis", "LockDog from Tip")

# --- collar
col = insert("v1_LockCollar", TIP - D_COL, ang(comps(asm)[HUB]) + HALF)
axis_and_distance(COL, D_COL, "LockCollar on Axis", "LockCollar from Tip")
if "LockCollar rides LockHub" not in mates(asm):
    zc = origin(comps(asm)[COL])[2]
    th_h = ang(comps(asm)[HUB])
    for label, off in (("negative control, 0 deg", 0.0), ("4.5 deg", HALF / 2), ("9 deg (convention)", HALF)):
        put_rot(comps(asm)[COL], th_h + off, zc); rebuild()
        c = comps(asm)[COL]
        print(f"  collar at hub {label}: collar-hub {math.degrees(wrap(ang(c) - th_h)):.3f} deg, Z {origin(c)[2]} -> hits {col_hits([COL]) or 'none'}")
    if col_hits([COL]):
        raise SystemExit("STOP: collar interferes at the 9 deg phase")
gear_mate(COL, HUB, "LockCollar rides LockHub")
# dog into the collar's phase before mating (same phase as hub)
if "LockCollar engages LockDog" not in mates(asm):
    d = comps(asm)[DOG]; th = ang(comps(asm)[COL]) - HALF
    put_rot(d, th, origin(d)[2]); rebuild()
    m = gear_mate(COL, DOG, "LockCollar engages LockDog")
    m = mates(asm)["LockCollar engages LockDog"]
    m.SetSuppression2(0, 1, None); rebuild()
cfgs = list(asm.GetConfigurationNames)
print("lock mates:"); [print("  ", mate_desc(asm, s, cfgs)) for n, s in mates(asm).items() if n.startswith("Lock")]
cs = comps(asm)
for n in (RS, HUB, DOG, COL):
    print(f"  {n:18} origin {origin(cs[n])} z-axis {zaxis(cs[n])} angle {math.degrees(ang(cs[n])):.4f}")
print("phase collar-hub", round(math.degrees(wrap(ang(cs[COL]) - ang(cs[HUB]))), 4), "| dog-hub", round(math.degrees(wrap(ang(cs[DOG]) - ang(cs[HUB]))), 4))
print("errors:", errors(asm) or "none")
print("interferences:", interferences(asm) or "none")
