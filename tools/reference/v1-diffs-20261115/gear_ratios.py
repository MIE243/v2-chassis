import sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
for title in sys.argv[3:]:
    d = app.GetFirstDocument; asm = None
    while d is not None:
        if d.GetTitle.lower().replace(".sldasm", "") == title.lower(): asm = d
        d = d.GetNext
    print("==", title, "found" if asm else "NOT OPEN")
    if asm is None: continue
    f = asm.FirstFeature
    while f is not None:
        if f.GetTypeName2 == "MateGroup":
            s = f.GetFirstSubFeature
            while s is not None:
                if s.GetTypeName2 in ("MateGear", "GearMate") or s.Name.lower().startswith("gearmate") or "belt" in s.Name.lower():
                    try:
                        g = s.GetDefinition
                        num, den, rev = g.GearRatioNumerator, g.GearRatioDenominator, g.Reverse
                        ents = []
                        m = s.GetSpecificFeature2
                        for i in range(m.GetMateEntityCount):
                            ents.append(m.MateEntity(i).ReferenceComponent.Name2)
                        print(f"  {s.Name:12} [{s.GetTypeName2}] {' <-> '.join(ents):40} ratio {num*1000:.3f} : {den*1000:.3f} (mm)  -> {num/den:.4f}   reverse={rev}")
                    except Exception as ex:
                        print(f"  {s.Name:12} [{s.GetTypeName2}] unreadable: {type(ex).__name__} {ex}")
                s = s.GetNextSubFeature
        f = f.GetNextFeature
