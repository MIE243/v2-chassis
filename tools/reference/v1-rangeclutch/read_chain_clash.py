r"""Read-only: Z extents and radial reach of the chain sub-assembly vs the mode sleeve, hub and sprocket dog, in the active configuration."""
import os, sys, math
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
asm = app.GetOpenDocumentByName(r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Transfer Case\v1_TransferCase.SLDASM")
print("active", asm.ConfigurationManager.ActiveConfiguration.Name, "| unsaved", bool(asm.GetSaveFlag))
for c in asm.GetComponents(False) or ():
    n = c.Name2
    if any(k in n for k in ("Sleeve_m1.25_N20", "v1_ModeHub", "Dog_m1.25_N20", "v1_Chain-1", "Sprocket", "sprocket")) and "/" not in n:
        b = [v * M for v in c.GetBox(False, False)]
        print(f"  {n:40} Z {b[2]:8.2f}..{b[5]:8.2f}  X {b[0]:8.2f}..{b[3]:8.2f}  Y {b[1]:8.2f}..{b[4]:8.2f}")
links = [c for c in asm.GetComponents(False) if c.Name2.startswith("v1_Chain-1/")]
near = []
for c in links:
    bx = c.GetBox(False, False)
    if bx is None: continue
    b = [v * M for v in bx]
    r = math.hypot((b[0] + b[3]) / 2, (b[1] + b[4]) / 2)
    if r < 30: near.append((round(r, 2), round(b[2], 2), round(b[5], 2), c.Name2.split("/")[-1]))
print("  chain parts with centre within 30 mm of the axis (centre r, Z from, Z to):")
for x in sorted(near): print("   ", x)
