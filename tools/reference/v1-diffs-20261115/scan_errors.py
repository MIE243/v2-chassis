import sys, os
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from win32com.client import VARIANT
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
def err(f):
    w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
    try:
        c = f.GetErrorCode2(w); return c, w.value
    except Exception as e:
        return "?", str(e)
def walk(f, depth, out):
    while f is not None:
        c, w = err(f)
        if (c not in (0, None)) or w:
            out.append(("  " * depth) + f"{f.Name} [{f.GetTypeName2}] error={c} warning={w}")
        sub = f.GetFirstSubFeature
        if sub is not None and f.GetTypeName2 in ("MateGroup", "MateReferenceGroupFolder", "FtrFolder", "HistoryFolder") :
            walk(sub, depth + 1, out)
        f = f.GetNextFeature if depth == 0 else f.GetNextSubFeature
d = app.GetFirstDocument
active = app.ActiveDoc
print("active document:", active.GetTitle if active else None)
while d is not None:
    out = []
    walk(d.FirstFeature, 0, out)
    vis = bool(d.Visible)
    if out or vis:
        print(f"== {d.GetTitle} | visible={vis} unsaved={bool(d.GetSaveFlag)} | {d.GetPathName}")
        for line in out: print(line)
        if d.GetType == 2:
            for c in d.GetComponents(True) or ():
                if c.IsSuppressed or (c.GetSuppression2 if hasattr(c,'GetSuppression2') else 2) == 0:
                    pass
    d = d.GetNext
