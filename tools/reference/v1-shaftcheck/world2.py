import sys, os
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M=1000.0
asm=app.GetOpenDocumentByName(r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\v1 Chassis Assembly.SLDASM")
WANT=["FD_Pinion"]
def W(a,p):
    return [a[0]*p[0]+a[3]*p[1]+a[6]*p[2]+a[9], a[1]*p[0]+a[4]*p[1]+a[7]*p[2]+a[10], a[2]*p[0]+a[5]*p[1]+a[8]*p[2]+a[11]]
def R(a,v):
    return [a[0]*v[0]+a[3]*v[1]+a[6]*v[2], a[1]*v[0]+a[4]*v[1]+a[7]*v[2], a[2]*v[0]+a[5]*v[1]+a[8]*v[2]]
for c in asm.GetComponents(False) or ():
    n=c.Name2
    if "Chain" in n or "Belt" in n or not any(w in n for w in WANT): continue
    a=c.Transform2.ArrayData
    a=[float(x) for x in a]
    bx=c.GetBox(False,False)
    print("==",n,"worldbox",[round(v*M,1) for v in bx] if bx else None)
    comp=c
    bodies=c.GetBodies3(0, swcom._out_long()) if False else None
    ms=c.GetModelDoc2
    seen={}
    for b in ms.GetBodies2(0,True) or ():
        for fc in b.GetFaces() or ():
            s=fc.GetSurface
            if not s.IsCylinder: continue
            pr=s.CylinderParams; r=pr[6]*M
            if r<3.0: continue
            o=[x*M for x in pr[0:3]]; d=pr[3:6]
            ow=W(a[:9]+[a[9]*M,a[10]*M,a[11]*M],o); dw=R(a,d)
            fb=fc.GetBox; pts=[[fb[i],fb[j],fb[k]] for i in (0,3) for j in (1,4) for k in (2,5)]
            zs=[W(a[:9]+[a[9]*M,a[10]*M,a[11]*M],[x*M for x in p])[2] for p in pts]
            # axis point at world: radial offset of axis from main axis
            key=(round(r,3),round(ow[0]-dw[0]/ (dw[2] or 1e-9)*ow[2] if abs(dw[2])>.5 else ow[0],2), round(ow[1]-dw[1]/(dw[2] or 1e-9)*ow[2] if abs(dw[2])>.5 else ow[1],2), tuple(round(abs(x),2) for x in dw))
            e=seen.setdefault(key,[1e9,-1e9]); e[0]=min(e[0],min(zs)); e[1]=max(e[1],max(zs))
    for k,v in sorted(seen.items()): print("   r=%s axisXY=(%s,%s) |dir|=%s  worldZ %.2f..%.2f"%(k+(v[0],v[1])))
