r"""(v1-centrelock copy) Read-only: pull every transfer-case part's tessellation (part frame, mm) and each component's placement out of the
open SolidWorks session, plus the centre diff gears. Writes cad.json next to this script. Opens v1_CentreDiff.SLDASM
read-only only if it is not open, and closes only what it opened (if unmodified). Changes nothing else.
python.exe extract.py <gear-generator src> <pid>"""
import base64, json, os, struct, sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
ROOT = r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis"
TC = os.path.join(ROOT, "Transfer Case", "v1_TransferCase.SLDASM")
CD = os.path.join(ROOT, "Differentials", "v1_CentreDiff.SLDASM")
Q = 200.0   # int16 units per mm


def call0(obj, name):
    v = getattr(obj, name)
    return v() if type(v).__name__ == "method" else v


meshes = {}


def tess(doc, key):
    if key in meshes:
        return
    pos, idx, nverts, ntri = [], [], 0, 0
    lo = [1e9] * 3; hi = [-1e9] * 3
    for b in doc.GetBodies2(0, True) or ():
        for f in b.GetFaces() or ():
            t = f.GetTessTriangles(True)
            if t is None:
                continue
            t = list(t)
            local = {}
            for i in range(0, len(t), 3):
                p = (round(t[i] * M * Q), round(t[i + 1] * M * Q), round(t[i + 2] * M * Q))
                if p not in local:
                    local[p] = nverts; nverts += 1; pos.extend(p)
                    for k in range(3):
                        lo[k] = min(lo[k], p[k] / Q); hi[k] = max(hi[k], p[k] / Q)
                idx.append(local[p])
            ntri += len(t) // 9
    big = nverts > 65535
    meshes[key] = {
        "pos": base64.b64encode(struct.pack(f"<{len(pos)}h", *pos)).decode(),
        "idx": base64.b64encode(struct.pack(f"<{len(idx)}{'I' if big else 'H'}", *idx)).decode(),
        "idx32": big, "verts": nverts, "tris": ntri,
        "box": [round(v, 2) for v in lo + hi],
    }
    print(f"  mesh {key:32} {nverts:7} verts {ntri:7} tris  box {meshes[key]['box']}")


def doc_of(comp):
    d = comp.GetModelDoc2
    if d is None:
        d = app.GetOpenDocumentByName(comp.GetPathName)
    return d


def walk(comp, out, depth=0):
    path = comp.GetPathName or ""
    key = os.path.splitext(os.path.basename(path))[0]
    xf = [float(v) for v in comp.Transform2.ArrayData]
    rec = {"name": comp.Name2, "part": key, "xf": [round(v, 6) for v in xf[:9]] + [round(v * M, 4) for v in xf[9:12]],
           "supp": bool(comp.IsSuppressed)}
    if path.lower().endswith(".sldprt"):
        d = doc_of(comp)
        if d is None:
            print("  no document for", comp.Name2); rec["nodoc"] = True
        else:
            tess(d, key)
        out.append(rec)
    else:
        rec["children"] = []
        for ch in comp.GetChildren or ():
            walk(ch, rec["children"], depth + 1)
        out.append(rec)


result = {"cd_assembly": "v1_CenterDiff_Assem.SLDASM (the user's centre diff, as referenced by v1 Chassis Assembly)"}
CDU = os.path.join(ROOT, "Differentials", "v1_CenterDiff_Assem.SLDASM")
cd = app.GetOpenDocumentByName(CDU)
if cd is None:
    raise SystemExit("STOP: v1_CenterDiff_Assem.SLDASM not open")
result["cd_config"] = cd.ConfigurationManager.ActiveConfiguration.Name
result["cd"] = []
for c in cd.GetComponents(True) or ():
    walk(c, result["cd"])
result["lock_parts_unplaced"] = []
for stem in ("v1_LockDog", "v1_LockHub", "v1_LockCollar"):
    d = app.GetOpenDocumentByName(os.path.join(ROOT, "Differentials", stem + ".SLDPRT"))
    if d is None:
        print("  not open:", stem); continue
    tess(d, stem); result["lock_parts_unplaced"].append(stem)
result["meshes"] = meshes
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cd.json")
with open(out, "w") as fh:
    json.dump(result, fh)
print("wrote", out, os.path.getsize(out) // 1024, "KB")
