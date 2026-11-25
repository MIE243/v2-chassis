import sys, os
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M=1000.
R=r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\Differentials\v1_CD_SideF.SLDPRT"
doc=app.GetOpenDocumentByName(R)
for b in doc.GetBodies2(0,True):
    print(b.Name, [round(x*M,2) for x in b.GetBodyBox()], "faces", len(b.GetFaces()))
    seen={}
    for f in b.GetFaces():
        s=f.GetSurface
        k="cyl" if s.IsCylinder else "plane" if s.IsPlane else "cone" if s.IsCone else "other"
        bx=[round(x*M,2) for x in f.GetBox]
        extra=""
        if k=="plane": 
            extra=tuple(round(x,2) for x in s.PlaneParams)
        if k=="cone": extra=[round(x*M,2) for x in s.ConeParams[:3]]+[round(s.ConeParams[6]*M,2)]
        if k in("plane","cone") or (k=="cyl" and s.CylinderParams[6]*M>2): print(" ",k,bx,extra)
