r"""Read-only: is v1_CD_Carrier-1 fixed, and what mates touch it (types, entities)."""
import sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
asm = app.GetOpenDocumentByName(r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Differentials\v1_CenterDiff_Assem.SLDASM")
print("open:", asm is not None, "| unsaved:", bool(asm.GetSaveFlag), "| config:", asm.ConfigurationManager.ActiveConfiguration.Name)
for c in asm.GetComponents(True) or ():
    print(f"  {c.Name2:24} fixed={bool(c.IsFixed)}")
f = asm.FirstFeature
while f is not None:
    if f.GetTypeName2 == "MateGroup":
        s = f.GetFirstSubFeature
        while s is not None:
            try:
                m = s.GetSpecificFeature2
                ents = []
                for i in range(m.GetMateEntityCount):
                    e = m.MateEntity(i); rc = e.ReferenceComponent
                    ents.append(f"{rc.Name2 if rc else 'asm'}:{e.ReferenceType2}")
                if any("Carrier" in x or "Lock" in x for x in ents):
                    print(f"  mate {s.Name:28} type {m.Type:2} {ents}")
            except Exception as ex:  # noqa: BLE001
                pass
            s = s.GetNextSubFeature
    f = f.GetNextFeature
