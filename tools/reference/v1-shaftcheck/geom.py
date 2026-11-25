import sys, os
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M=1000.0
R=r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis"
parts=["Transfer Case\\v1_InDog","Transfer Case\\v1_RangeHub","Transfer Case\\v1_ModeHub","Differentials\\v1_LockHub","Transfer Case\\v1_Sprocket_Front","Differentials\\v1_FD_Pinion","Differentials\\v1_CD_Carrier","Differentials\\v1_CD_SideF"]
for p in parts:
    doc=app.GetOpenDocumentByName(os.path.join(R,p+".SLDPRT"))
    print("=====",p)
    f=doc.FirstFeature; fs=[]
    while f is not None:
        fs.append(f"{f.Name}[{f.GetTypeName2}]"); f=f.GetNextFeature
    print(" features:", [x for x in fs if not any(k in x for k in ("Plane","Origin","Annotations","Material","Sensor","Equation","Lights","Cameras","History","Design Binder","Selection"))])
    for b in doc.GetBodies2(0,True) or ():
        bb=[round(v*M,3) for v in b.GetBodyBox()]
        print(" body",b.Name,"box",bb)
        cyl={}
        for fc in b.GetFaces() or ():
            s=fc.GetSurface
            if s.IsCylinder:
                pr=s.CylinderParams
                bx=[round(v*M,2) for v in fc.GetBox]
                key=(round(pr[6]*M,3),round(pr[0]*M,2),round(pr[1]*M,2),round(pr[3],2),round(pr[4],2),round(pr[5],2))
                e=cyl.setdefault(key,[1e9,-1e9]); e[0]=min(e[0],bx[2]); e[1]=max(e[1],bx[5])
        for k,v in sorted(cyl.items()): print("  cyl r=%s origin(%s,%s) dir(%s,%s,%s) z %s..%s"%(k+tuple(v)))
