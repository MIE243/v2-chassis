import sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M=1000.0
d = app.GetFirstDocument
while d is not None:
    print("DOC", d.GetPathName, "unsaved", bool(d.GetSaveFlag))
    d = d.GetNext
