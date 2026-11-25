r"""Read-only: open documents; v1_CentreDiff.SLDASM components, transforms, mates (type, entities, values, flips,
gear definitions), configurations, layout part equations/features. Changes nothing."""
import os, sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from win32com.client import VARIANT
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
D = r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Differentials"
print("open documents:")
d = app.GetFirstDocument
while d is not None:
    print(f"   {d.GetPathName}  unsaved={bool(d.GetSaveFlag)} visible={d.Visible}")
    d = d.GetNext
asm = app.GetOpenDocumentByName(os.path.join(D, "v1_CentreDiff.SLDASM"))
if asm is None:
    raise SystemExit("v1_CentreDiff.SLDASM not open")
print("CD unsaved:", bool(asm.GetSaveFlag), "| active", asm.ConfigurationManager.ActiveConfiguration.Name,
      "| configs", list(asm.GetConfigurationNames), "| title", asm.GetTitle)
for c in asm.GetComponents(True) or ():
    a = [float(v) for v in c.Transform2.ArrayData]
    print(f"  comp {c.Name2:28} {c.GetPathName}\n       rot {[round(v,4) for v in a[:9]]} t {[round(v*M,4) for v in a[9:12]]} fixed={c.IsFixed} supp={c.IsSuppressed}")
cfgs = list(asm.GetConfigurationNames)
f = asm.FirstFeature
while f is not None:
    if f.GetTypeName2 == "MateGroup":
        s = f.GetFirstSubFeature
        while s is not None:
            m = s.GetSpecificFeature2
            ents = []
            try:
                for i in range(m.GetMateEntityCount):
                    e = m.MateEntity(i); c = e.ReferenceComponent
                    r = e.Reference
                    rn = None
                    try: rn = r.Name
                    except Exception: pass
                    ents.append((c.Name2 if c else "asm", e.ReferenceType2, rn))
            except Exception as ex:
                ents = str(ex)
            w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
            code = s.GetErrorCode2(w)
            vals = None
            dd = s.GetFirstDisplayDimension
            if dd is not None:
                vals = [round(v * M, 4) for v in dd.GetDimension2(0).GetSystemValue3(2, cfgs)]
            extra = ""
            try:
                g = s.GetDefinition
                extra = f"ratio {g.GearRatioNumerator}:{g.GearRatioDenominator} reverse {g.Reverse}"
            except Exception:
                pass
            try: t = m.Type; fl = m.Flipped; al = m.Alignment
            except Exception: t = fl = al = "?"
            print(f"  mate {s.Name:30} type {t} align {al} flipped {fl} ents {ents} vals {vals} supp {list(s.IsSuppressed2(2, cfgs))} err {code},{w.value} {extra}")
            s = s.GetNextSubFeature
    f = f.GetNextFeature
lay = [c for c in asm.GetComponents(True) if "Layout" in c.Name2][0]
ld = lay.GetModelDoc2
print("layout doc:", ld.GetPathName, "unsaved", bool(ld.GetSaveFlag))
em = ld.GetEquationMgr
for i in range(em.GetCount):
    print("  eq:", em.Equation(i))
ff = ld.FirstFeature
while ff is not None:
    t = ff.GetTypeName2
    dims = []
    dd = ff.GetFirstDisplayDimension
    while dd is not None:
        dm = dd.GetDimension2(0); dims.append((dm.FullName, round(dm.SystemValue * M, 4)))
        dd = ff.GetNextDisplayDimension(dd)
    print(f"  feat {ff.Name:30} {t:22} {dims}")
    ff = ff.GetNextFeature
for c in asm.GetComponents(True):
    if "Layout" in c.Name2: continue
    pd = c.GetModelDoc2
    print("=== part", c.Name2, "unsaved", bool(pd.GetSaveFlag))
    em = pd.GetEquationMgr
    for i in range(em.GetCount):
        print("  eq:", em.Equation(i))
    ff = pd.FirstFeature; names = []
    while ff is not None:
        if ff.GetTypeName2 in ("RefAxis", "RefPlane", "RefPoint"): names.append((ff.Name, ff.GetTypeName2))
        ff = ff.GetNextFeature
    print("  refs:", names)
