import sys, math
SRC, PID, TITLE = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
from gear_generator.swcom import call
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0; APEX = -252.75
d = app.GetFirstDocument; asm = None
while d is not None:
    if d.GetTitle == TITLE: asm = d
    d = d.GetNext
def member(o, n):
    v = call(o, n); return v() if type(v).__name__ in ("method", "function") else v
mgr = call(asm, "InterferenceDetectionManager")
for n, v in (("TreatCoincidenceAsInterference", False), ("TreatSubAssembliesAsComponents", False), ("IncludeMultibodyPartInterferences", True), ("MakeInterferingPartsTransparent", False), ("CreateFastenersFolder", False), ("IgnoreHiddenBodies", True), ("ShowIgnoredInterferences", False), ("UseTransform", False)):
    setattr(mgr, n, v)
try:
    for it in list(member(mgr, "GetInterferences") or ()):
        comps = [str(call(c, "Name2")).split("/")[-1] for c in (member(it, "Components") or ())]
        vol = float(member(it, "Volume")) * 1e9
        body = None
        for name in ("GetInterferenceBody", "Body", "InterferenceBody"):
            try:
                body = member(it, name)
                if body is not None: break
            except Exception as e:
                pass
        if body is None:
            print(f"{vol:8.2f} mm3 {comps}: no body"); continue
        b = list(member(body, "GetBodyBox"))
        lo = [v * M for v in b[0:3]]; hi = [v * M for v in b[3:6]]
        # distances from the cone tip: along X (axle), and radius from the axle (Y,Z about z=APEX)
        rmax = max(math.hypot(y, z - APEX) for y in (lo[1], hi[1]) for z in (lo[2], hi[2]))
        rmin_y = min(abs(lo[1]), abs(hi[1])) if lo[1] * hi[1] > 0 else 0.0
        print(f"{vol:8.2f} mm3 {comps}: X {lo[0]:.2f}..{hi[0]:.2f}  Y {lo[1]:.2f}..{hi[1]:.2f}  Z-tip {lo[2]-APEX:.2f}..{hi[2]-APEX:.2f}  (radius from axle up to {rmax:.2f})")
finally:
    mgr.Done()
r = [c for c in asm.GetComponents(False) if str(call(c, "Name2")).endswith("v1_FD_Ring-1")]
for c in r:
    bx = c.GetBox(False, False); print("ring box X", round(bx[0]*M,2), round(bx[3]*M,2), "Y", round(bx[1]*M,2), round(bx[4]*M,2))
