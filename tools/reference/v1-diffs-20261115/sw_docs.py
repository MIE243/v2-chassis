r"""List, or close, the documents open in the running SolidWorks.
python.exe sw_docs.py <gear-generator src> <pid> list
python.exe sw_docs.py <gear-generator src> <pid> close <folder> [<folder> ...]
'close' closes only documents saved under one of the folders and with no unsaved changes; anything modified is
left open and reported. CloseDoc discards silently, so the save flag is checked first, every time."""
import os
import sys
SRC, PID, ACTION = sys.argv[1], int(sys.argv[2]), sys.argv[3]
FOLDERS = [os.path.normcase(os.path.normpath(f)) + os.sep for f in sys.argv[4:]]
sys.path.insert(0, SRC)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom  # noqa: E402
from gear_generator import swcom  # noqa: E402

pythoncom.CoInitialize()
cands = [c for c in swcom.find_candidates() if c.pid == PID]
if not cands:
    print("STOP: SolidWorks", PID, "not reachable"); raise SystemExit(2)
app = cands[0].app
KIND = {1: "part", 2: "assembly", 3: "drawing"}


def docs():
    out = []
    d = app.GetFirstDocument
    while d is not None:
        out.append(d)
        d = d.GetNext
    return out


def describe(d):
    path = d.GetPathName or ""
    return dict(title=d.GetTitle, path=path, kind=KIND.get(d.GetType, d.GetType), dirty=bool(d.GetSaveFlag),
                visible=bool(d.Visible))


listing = [describe(d) for d in docs()]
for x in listing:
    print(f"{x['kind']:9} dirty={x['dirty']!s:5} visible={x['visible']!s:5} {x['title']} | {x['path']}")

if ACTION in ("close", "close-parts"):
    def ours(path):
        return path and any(os.path.normcase(os.path.normpath(path)).startswith(f) for f in FOLDERS)
    # assemblies first, so their parts are no longer held by an open assembly when their turn comes
    order = sorted(docs(), key=lambda d: 0 if d.GetType == 2 else 1)
    for d in order:
        x = describe(d)
        if ACTION == "close-parts" and x["kind"] != "part":
            print("KEEP (assembly):", x["title"])
            continue
        if not ours(x["path"]):
            print("KEEP (not in the folders):", x["title"], x["path"])
            continue
        if x["dirty"]:
            print("KEEP (unsaved changes):", x["title"])
            continue
        app.CloseDoc(x["title"])
        print("closed", x["title"])
    print("--- after")
    for x in (describe(d) for d in docs()):
        print(f"{x['kind']:9} dirty={x['dirty']!s:5} visible={x['visible']!s:5} {x['title']} | {x['path']}")
