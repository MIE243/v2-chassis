r"""Read-only apart from switching configuration (restores the configuration that was active): per configuration
record every component's Transform2 to xf_<tag>.json (tag = argv[3]), print origins, z axes, angles about Z, the
dog-carrier / collar-dog phases and mate errors."""
from lockcommon import *  # noqa: F401,F403
import json
TAG = sys.argv[3]
asm = app.GetOpenDocumentByName(CDU)
app.ActivateDoc3(asm.GetTitle, False, 0, out())
start = asm.ConfigurationManager.ActiveConfiguration.Name
res = {"active": start, "cfg": {}}
for k in asm.GetConfigurationNames:
    asm.ShowConfiguration2(k); asm.EditRebuild3
    cs = comps(asm)
    res["cfg"][k] = {n: xf(c) for n, c in cs.items()}
    print(f"[{k}] errors {errors(asm) or 'none'}")
    for n, c in cs.items():
        print(f"   {n:18} origin {origin(c)} z {zaxis(c)} angZ {math.degrees(ang(c)):9.4f}")
    a = lambda n: math.degrees(ang(cs[n]))  # noqa: E731
    print(f"   dog-carrier {a('v1_LockDog-1') - a('v1_CD_Carrier-1'):.4f} | collar-dog {a('v1_LockCollar-1') - a('v1_LockDog-1'):.4f}"
          f" | collar-hub {a('v1_LockCollar-1') - a('v1_LockHub-1'):.4f}")
asm.ShowConfiguration2(start); asm.EditRebuild3
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"xf_{TAG}.json"), "w"), indent=1)
print("active", asm.ConfigurationManager.ActiveConfiguration.Name, "| CD unsaved", bool(asm.GetSaveFlag))
for p, u in open_docs():
    if u: print("  UNSAVED", p)
