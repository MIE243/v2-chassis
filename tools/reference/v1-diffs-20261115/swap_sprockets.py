r"""Swap the two Toolbox sprockets in v1_TransferCase.SLDASM for standalone repo parts with exact metric bores.

For each sprocket component: save a copy of the in-memory Toolbox part to Transfer Case\<name>.SLDPRT, open the copy,
keep only that component's configuration (design table first, then the others), mark it not-a-Toolbox-part, cut the
bore to its metric size through all both ways (checked by the volume removed), save. Then select the component and
ReplaceComponents2 with the copy (same configuration name, mates re-attached), check mates and position, and save the
assembly only if it had no unsaved changes of its own before.
python.exe swap_sprockets.py <gear-generator src> <pid>"""
import math
import os
import sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom  # noqa: E402
from gear_generator import swcom  # noqa: E402
from gear_generator.swcom import call  # noqa: E402

pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
TC = r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Transfer Case"
ASM_PATH = os.path.join(TC, "v1_TransferCase.SLDASM")
PLAN = {  # component name -> (new file stem, bore mm)
    "precision roller chain sprocket_ai-1": ("v1_Sprocket_Drive", 14.0),
    "precision roller chain sprocket_ai-3": ("v1_Sprocket_Front", 8.0),
}
NULL = swcom._null_dispatch  # noqa: SLF001


def out():
    return swcom._out_long()  # noqa: SLF001


def member(obj, name):
    v = call(obj, name)
    return v() if type(v).__name__ in ("method", "function") else v


def volume_mm3(doc):
    mp = member(call(doc, "Extension"), "CreateMassProperty")
    return float(mp.Volume) * 1e9


asm = app.GetOpenDocumentByName(ASM_PATH)
if asm is None:
    print("STOP: v1_TransferCase.SLDASM is not open"); raise SystemExit(2)
asm_was_dirty = bool(asm.GetSaveFlag)
print("assembly", asm.GetTitle, "| had unsaved changes before:", asm_was_dirty)
comps = {c.Name2: c for c in (asm.GetComponents(True) or ())}
for name in PLAN:
    if name not in comps:
        print("STOP: component not found:", name); raise SystemExit(3)

made = {}
for name, (stem, bore) in PLAN.items():
    comp = comps[name]
    cfg = comp.ReferencedConfiguration
    src_doc = comp.GetModelDoc2
    dest = os.path.join(TC, stem + ".SLDPRT")
    if os.path.exists(dest):
        doc = app.GetOpenDocumentByName(dest)
        done = False
        if doc is not None:
            for b in doc.GetBodies2(0, True) or ():
                for face in b.GetFaces() or ():
                    s = face.GetSurface
                    if s.IsCylinder and abs(list(s.CylinderParams)[6] * M - bore / 2.0) < 1e-3:
                        done = True
        if not done:
            print("STOP: already exists and not from this run:", dest); raise SystemExit(4)
        e1, e2 = out(), out()
        print(f"--- {name}: copy already made and cut in this run; saved:", doc.Save3(1, e1, e2),
              "| configs:", list(doc.GetConfigurationNames or ()), "| toolbox flag:", doc.Extension.ToolboxPartType,
              "| volume", round(volume_mm3(doc), 2))
        made[name] = (dest, cfg, doc)
        continue
    xf = comp.Transform2.ArrayData
    cols = [xf[0:3], xf[3:6], xf[6:9]]                      # where part X, Y, Z go in the assembly
    axis_i = max(range(3), key=lambda i: abs(cols[i][2]))    # the part axis that lies along assembly Z
    print(f"--- {name}: config {cfg}; part axis {'XYZ'[axis_i]} lies along assembly Z ({cols[axis_i][2]:+.3f})")
    e1, e2 = out(), out()
    call(call(src_doc, "Extension"), "SaveAs3", dest, 0, 1 | 2, NULL(), NULL(), e1, e2)   # silent | copy
    print("  saved a copy from the open Toolbox part ->", dest, "exists:", os.path.exists(dest))
    spec = app.GetOpenDocSpec(dest); spec.Silent = True
    doc = app.OpenDoc7(spec)
    if doc is None:
        print("STOP: copy did not open, error", spec.Error); raise SystemExit(5)
    doc.ShowConfiguration2(cfg)
    if doc.ConfigurationManager.ActiveConfiguration.Name != cfg:
        print("STOP: could not activate", cfg); raise SystemExit(6)
    try:
        doc.DeleteDesignTable()
    except Exception:  # noqa: BLE001
        pass
    for _ in range(6):
        names = list(doc.GetConfigurationNames or ())
        if len(names) <= 1:
            break
        for n in names:
            if n != cfg:
                try:
                    doc.DeleteConfiguration2(n)
                except Exception:  # noqa: BLE001
                    pass
    names = list(doc.GetConfigurationNames or ())
    print("  configurations left:", names)
    ext = call(doc, "Extension")
    before_tb = ext.ToolboxPartType
    ext.ToolboxPartType = 0          # swNotAToolboxPart
    print("  Toolbox flag:", before_tb, "->", ext.ToolboxPartType)
    # the plane square to the sprocket axis: Front (normal Z), Top (normal Y), Right (normal X)
    plane = None
    f = doc.FirstFeature
    while f is not None and plane is None:
        if f.GetTypeName2 == "RefPlane":
            a = f.GetSpecificFeature2.Transform.ArrayData
            if abs(abs(a[6 + axis_i]) - 1.0) < 1e-6 and max(abs(v) for v in a[9:12]) < 1e-9:
                plane = f
        f = f.GetNextFeature
    print("  bore sketch on", plane.Name)
    v0 = volume_mm3(doc)
    call(doc, "ClearSelection2", True)
    plane.Select2(False, 0)
    sm = call(doc, "SketchManager")
    sm.InsertSketch(True)
    sm.CreateCircleByRadius(0.0, 0.0, 0.0, bore / 2.0 / M)
    sm.InsertSketch(True)
    sketch = None
    f = doc.FirstFeature
    while f is not None:
        if f.GetTypeName2 == "ProfileFeature":
            sketch = f
        f = f.GetNextFeature
    call(doc, "ClearSelection2", True)
    sketch.Select2(False, 0)
    cut = call(call(doc, "FeatureManager"), "FeatureCut4", False, False, False, 9, 9, 0.01, 0.01, False, False,
               False, False, 0.0, 0.0, False, False, False, False, False, True, True, True, True, False, 0, 0.0,
               False, False)
    call(doc, "ClearSelection2", True)
    if cut is None:
        print("  STOP: the bore cut made nothing"); raise SystemExit(7)
    cut.Name = f"Bore {bore:g} mm"
    doc.EditRebuild3  # late binding runs it on access
    v1 = volume_mm3(doc)
    print(f"  bore cut: volume {v0:.2f} -> {v1:.2f} mm^3 (removed {v0 - v1:.2f})")
    e1, e2 = out(), out()
    ok = doc.Save3(1, e1, e2)
    print("  saved:", ok, "| unsaved now:", bool(doc.GetSaveFlag))
    made[name] = (dest, cfg, doc)

# replace in the assembly
errs = out()
app.ActivateDoc3(asm.GetTitle, False, 0, errs)
for name, (dest, cfg, doc) in made.items():
    comp = {c.Name2: c for c in (asm.GetComponents(True) or ())}[name]
    call(asm, "ClearSelection2", True)
    sel = comp.Select4(False, NULL(), False)
    ok = asm.ReplaceComponents2(dest, cfg, False, 0, True)   # this instance only, match config name, re-attach mates
    print(f"replace {name} -> {os.path.basename(dest)}: selected {sel}, returned {ok}")
call(asm, "ClearSelection2", True)
asm.EditRebuild3  # late binding runs it on access

print("--- after:")
for c in asm.GetComponents(True) or ():
    p = c.GetPathName or ""
    if "procket" in p.lower():
        bx = c.GetBox(False, False)
        print(f"  {c.Name2:28} {os.path.basename(p):24} config {c.ReferencedConfiguration}  "
              f"X {bx[0]*M:.2f}..{bx[3]*M:.2f}  Y {bx[1]*M:.2f}..{bx[4]*M:.2f}  Z {bx[2]*M:.2f}..{bx[5]*M:.2f}")
bad = []
f = asm.FirstFeature
while f is not None:
    if f.GetTypeName2 == "MateGroup":
        s = f.GetFirstSubFeature
        while s is not None:
            code = s.GetErrorCode2
            code = code[0] if isinstance(code, tuple) else code
            if code:
                bad.append((s.Name, code))
            s = s.GetNextSubFeature
    f = f.GetNextFeature
print("mates with errors:", bad or "none")
if not asm_was_dirty and not bad:
    e1, e2 = out(), out()
    print("assembly saved:", asm.Save3(1, e1, e2), "| unsaved now:", bool(asm.GetSaveFlag))
else:
    print("assembly NOT saved (it had changes before, or a mate is in error)")
for name, (dest, cfg, doc) in made.items():
    if not doc.GetSaveFlag:
        app.CloseDoc(doc.GetTitle)
print("done")
