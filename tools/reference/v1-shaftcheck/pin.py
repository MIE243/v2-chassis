import sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
doc=app.GetOpenDocumentByName(r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Differentials\v1_FD_Pinion.SLDPRT")
b=list(doc.GetBodies2(0,True))[0]
for f in b.GetFaces():
    s=f.GetSurface; bx=[round(x*1000,2) for x in f.GetBox]
    if abs(bx[3]-bx[0])<9 and abs(bx[4]-bx[1])<9:
        print("plane" if s.IsPlane else "cone" if s.IsCone else "cyl" if s.IsCylinder else "other", bx)
