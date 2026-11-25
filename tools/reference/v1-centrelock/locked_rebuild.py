r"""In Locked: read mate errors, then ForceRebuild3(TopOnly=True) and read again; positions compared to xf_aftermates.
Ends on Default. Saves nothing."""
from lockcommon import *  # noqa: F401,F403
import json
asm = app.GetOpenDocumentByName(CDU)
app.ActivateDoc3(asm.GetTitle, False, 0, out())
ref = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "xf_aftermates.json")))["cfg"]
asm.ShowConfiguration2("Locked"); asm.EditRebuild3
print("Locked errors before:", errors(asm) or "none")
print("ForceRebuild3(True) ->", asm.ForceRebuild3(True))
print("Locked errors after:", errors(asm) or "none")
w = max(max(abs(x - y) for x, y in zip(xf(c), ref["Locked"][n])) for n, c in comps(asm).items())
print("max diff to aftermates", w)
asm.ShowConfiguration2("Default"); asm.EditRebuild3
print("Default errors:", errors(asm) or "none")
for p, u in open_docs():
    if u: print("  UNSAVED", p)
