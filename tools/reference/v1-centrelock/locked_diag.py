r"""Diagnose the Locked-configuration mate warnings (read-only apart from config switching): per configuration the
"LockDog keyed to Carrier" angle value, the dog-carrier angle, mate warnings; GetWhatsWrong in Locked. Ends on Default."""
from lockcommon import *  # noqa: F401,F403
from lockcommon import _dynamic
asm = app.GetOpenDocumentByName(CDU)
app.ActivateDoc3(asm.GetTitle, False, 0, out())
CFGS = list(asm.GetConfigurationNames)
for k in CFGS:
    asm.ShowConfiguration2(k); asm.EditRebuild3
    m = mates(asm)["LockDog keyed to Carrier"]
    d = m.GetFirstDisplayDimension.GetDimension2(0)
    cs = comps(asm)
    print(f"[{k}] angle dim {math.degrees(d.SystemValue):.4f} | all cfgs {[round(math.degrees(v), 4) for v in d.GetSystemValue3(2, CFGS)]}"
          f" | dog-carrier {math.degrees(ang(cs['v1_LockDog-1']) - ang(cs['v1_CD_Carrier-1'])):.4f} | warnings {len(errors(asm))}")
asm.ShowConfiguration2("Locked"); asm.EditRebuild3
try:
    ext = asm.Extension
    r = ext.GetWhatsWrongCount
    print("WhatsWrong count", r)
    ole = ext._oleobj_
    res = ole.InvokeTypes(ole.GetIDsOfNames("GetWhatsWrong"), 0, pythoncom.DISPATCH_METHOD, (11, 0),
                          ((16396, 3), (16396, 3), (16396, 3)), None, None, None)
    for f in res[1]:
        f = _dynamic.Dispatch(f); print("   wrong:", f.Name, f.GetTypeName2)
except Exception as ex:  # noqa: BLE001
    print("GetWhatsWrong failed:", ex)
asm.ShowConfiguration2("Default"); asm.EditRebuild3
