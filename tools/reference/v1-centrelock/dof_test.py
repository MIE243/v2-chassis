r"""DOF test, per configuration (argv[3] optional: comma list of configs). For each test: put a +10 deg rotation about
world Z on one component (Transform2), rebuild, read where everything went, then put EVERY component back to its
recorded transform and rebuild; verify the restore. Tests: carrier turned; rear side gear turned.
Per component: rotation about world Z (Z-axis parts) / spider orbit + spin about own axis; also origin shift.
Kinematic check (open diff, all about world +Z): dF + dR = 2 dC. Ends on Default. Saves nothing."""
from lockcommon import *  # noqa: F401,F403
asm = app.GetOpenDocumentByName(CDU)
app.ActivateDoc3(asm.GetTitle, False, 0, out())
CFGS = sys.argv[3].split(",") if len(sys.argv) > 3 else list(asm.GetConfigurationNames)
CAR, RS, FS = "v1_CD_Carrier-1", "v1_CD_Side-1", "v1_CD_SideF-2"
T = math.radians(10.0)


def mat(a): return [[a[0], a[3], a[6]], [a[1], a[4], a[7]], [a[2], a[5], a[8]]]   # columns = part X, Y, Z
def mm(A, B): return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def tr(A): return [list(r) for r in zip(*A)]
def rz(t): return [[math.cos(t), -math.sin(t), 0.0], [math.sin(t), math.cos(t), 0.0], [0.0, 0.0, 1.0]]


def axis_angle(R):
    c = max(-1.0, min(1.0, (R[0][0] + R[1][1] + R[2][2] - 1) / 2)); th = math.acos(c)
    if th < 1e-9: return [0.0, 0.0, 0.0], 0.0
    v = [R[2][1] - R[1][2], R[0][2] - R[2][0], R[1][0] - R[0][1]]; n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [round(x / n, 4) for x in v], math.degrees(th)


def rot_world_z(a, t):
    R = mm(rz(t), mat(a)); p = [sum(rz(t)[i][k] * a[9 + k] for k in range(3)) for i in range(3)]
    return [R[0][0], R[1][0], R[2][0], R[0][1], R[1][1], R[2][1], R[0][2], R[1][2], R[2][2], p[0], p[1], p[2]] + list(a[12:16])


def report(base, tag):
    cs = comps(asm); res = {}
    dC = None
    for n in sorted(cs):
        a, b = xf(cs[n]), base[n]
        D = mm(mat(a), tr(mat(b)))
        dz = math.degrees(math.atan2(D[1][0], D[0][0]))
        shift = round(max(abs(a[9 + k] - b[9 + k]) for k in range(3)) * M, 4)
        if "Spider" in n:   # orbit = rotation of the spider axis about Z; spin = what is left about its own axis
            ax0, ax1 = b[6:9], a[6:9]
            orbit = math.degrees(math.atan2(ax0[0] * ax1[1] - ax0[1] * ax1[0], ax0[0] * ax1[0] + ax0[1] * ax1[1]))
            resid = mm(rz(-math.radians(orbit)), D); axr, spin = axis_angle(resid)
            res[n] = orbit
            print(f"     {n:18} orbit {orbit:8.4f} | spin {spin:8.4f} about {axr} | origin shift {shift}")
        else:
            pure = abs(D[2][2] - 1) < 1e-9
            res[n] = dz
            print(f"     {n:18} turned {dz:8.4f} about world Z{'' if pure else ' (NOT pure Z!)'} | origin shift {shift}")
    print(f"     errors {errors(asm) or 'none'} | dF + dR - 2 dC = {res[FS] + res[RS] - 2 * res[CAR]:.4f}")
    return res


def restore(base):
    for attempt in range(3):
        cs = comps(asm)
        for n, c in cs.items(): put_xf(c, base[n])
        asm.EditRebuild3
        worst = max(max(abs(x - y) for x, y in zip(xf(c), base[n])) for n, c in comps(asm).items())
        if worst < 1e-9: return attempt + 1, worst
    return None, worst


ok = True
for k in CFGS:
    asm.ShowConfiguration2(k); asm.EditRebuild3
    base = {n: xf(c) for n, c in comps(asm).items()}
    print(f"===== [{k}] active {asm.ConfigurationManager.ActiveConfiguration.Name} | errors {errors(asm) or 'none'}")
    for who in (CAR, RS):
        put_xf(comps(asm)[who], rot_world_z(base[who], T)); asm.EditRebuild3
        print(f"  test: {who} pushed +10 deg about Z, rebuilt ->")
        report(base, who)
        n, w = restore(base)
        print(f"  restored in {n} pass(es), worst diff {w:.2e} | errors {errors(asm) or 'none'}")
        if n is None: ok = False; print("  RESTORE FAILED"); break  # noqa: E702
    if not ok: break
asm.ShowConfiguration2("Default"); asm.EditRebuild3
print("active", asm.ConfigurationManager.ActiveConfiguration.Name, "| all restored", ok)
for p, u in open_docs():
    if u: print("  UNSAVED", p)
