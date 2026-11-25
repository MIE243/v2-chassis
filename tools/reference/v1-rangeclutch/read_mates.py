r"""Read-only: the range sleeve's mates in v1_TransferCase.SLDASM: type, entities, per-config value and suppression,
and the gear mates' ratio/reverse."""
import sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from win32com.client import VARIANT
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
asm = app.GetOpenDocumentByName(r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Transfer Case\v1_TransferCase.SLDASM")
print("unsaved:", bool(asm.GetSaveFlag), "| active", asm.ConfigurationManager.ActiveConfiguration.Name)
cfgs = list(asm.GetConfigurationNames)
print("configs:", cfgs)
f = asm.FirstFeature
while f is not None:
    if f.GetTypeName2 == "MateGroup":
        s = f.GetFirstSubFeature
        while s is not None:
            if any(k in s.Name for k in ("RangeSlv", "ModeSlv")):
                m = s.GetSpecificFeature2
                ents = []
                for i in range(m.GetMateEntityCount):
                    e = m.MateEntity(i)
                    c = e.ReferenceComponent
                    ents.append((c.Name2 if c else "asm", e.ReferenceType2))
                sup = s.IsSuppressed2(2, cfgs)
                d = s.GetFirstDisplayDimension
                vals = None
                if d is not None:
                    dim = d.GetDimension2(0)
                    vals = [round(v * 1000, 3) for v in dim.GetSystemValue3(2, cfgs)]
                extra = ""
                try:
                    dd = s.GetDefinition
                    extra = f"ratio {dd.GearRatioNumerator}:{dd.GearRatioDenominator} reverse {dd.Reverse}"
                except Exception as ex:  # noqa: BLE001
                    extra = ""
                print(f"  {s.Name:28} type {m.Type:2} flipped {m.Flipped!s:5} ents {ents} supp {list(sup)} vals {vals} {extra}")
            s = s.GetNextSubFeature
    f = f.GetNextFeature
lay = [c for c in asm.GetComponents(True) if c.Name2.startswith("v1_TransferCase_Layout")][0]
ff = lay.FirstFeature
names = []
while ff is not None:
    if ff.GetTypeName2 in ("RefAxis", "RefPlane"): names.append(ff.Name)
    ff = ff.GetNextFeature
print("layout axes/planes:", names)
