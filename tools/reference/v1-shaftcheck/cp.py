import sys, os
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M=1000.
doc=app.GetOpenDocumentByName(r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Differentials\v1_CD_SideF.SLDPRT")
b=list(doc.GetBodies2(0,True))[0]
faces=list(b.GetFaces())
for z in (9.5,11,13,15,16.5,19,21):
    best=None
    for f in faces:
        q=f.GetClosestPointOn(0,0,z/M)
        if not q: continue
        d=((q[0])**2+(q[1])**2+(q[2]-z/M)**2)**.5*M
        if best is None or d<best[0]:
            s_=f.GetSurface
            best=(d,[round(x*M,2) for x in q],"plane" if s_.IsPlane else "cone" if s_.IsCone else "cyl" if s_.IsCylinder else "other")
    print(z,best)
