import sys, os
SRC, PID, TITLE = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
MATE = {0: "coincident", 1: "concentric", 2: "perpendicular", 3: "parallel", 4: "tangent", 5: "distance", 6: "angle",
        7: "unknown", 8: "symmetric", 9: "cam", 10: "gear", 11: "width", 12: "lock-to-sketch", 13: "rack-pinion",
        14: "max", 15: "min", 16: "lock", 17: "screw", 18: "linear-coupler", 19: "universal joint", 20: "coord sys",
        21: "slot", 22: "hinge", 23: "slider", 24: "profile center", 25: "magnetic"}
d = app.GetFirstDocument; asm = None
while d is not None:
    if d.GetTitle in (TITLE, TITLE + ".SLDASM"): asm = d
    d = d.GetNext
print("document:", asm.GetTitle, "| unsaved:", bool(asm.GetSaveFlag))
for c in asm.GetComponents(True) or ():
    a = c.Transform2.ArrayData
    print(f"  {c.Name2:22} {os.path.basename(c.GetPathName):22} fixed={bool(c.IsFixed)!s:5} own Z {tuple(round(v,3) for v in a[6:9])} origin {tuple(round(v*M,2) for v in a[9:12])}")
print("mates:")
f = asm.FirstFeature
while f is not None:
    if f.GetTypeName2 == "MateGroup":
        sub = f.GetFirstSubFeature
        while sub is not None:
            try:
                mate = sub.GetSpecificFeature2
                kind = MATE.get(mate.Type, mate.Type)
                ents = []
                for i in range(mate.GetMateEntityCount):
                    e = mate.MateEntity(i)
                    comp = e.ReferenceComponent
                    ents.append(f"{comp.Name2 if comp else '?'}:{e.ReferenceType2}")
                extra = ""
                if kind == "gear":
                    try: extra = f" ratio {round(mate.GearRatioNumerator, 3)}:{round(mate.GearRatioDenominator, 3)} reversed={mate.Reverse}"
                    except Exception: pass
                sup = sub.IsSuppressed2(1, None)[0] if isinstance(sub.IsSuppressed2(1, None), tuple) else sub.IsSuppressed2(1, None)
                err = sub.GetErrorCode2 if hasattr(sub, "GetErrorCode2") else ""
                print(f"  {sub.Name:28} {kind:13} {'  &  '.join(ents)}{extra}  suppressed={sup} err={err}")
            except Exception as ex:
                print("  ", sub.Name, "(could not read:", type(ex).__name__, ex, ")")
            sub = sub.GetNextSubFeature
    f = f.GetNextFeature
