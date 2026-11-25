import sys, os
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from gear_generator import swcom
from gear_generator.swcom import call
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
asm=app.GetOpenDocumentByName(r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis\v1 Chassis Assembly.SLDASM")
comps={c.Name2.split("/")[-1]:c for c in asm.GetComponents(False)}
def body(n):
    c=comps[n]
    pb=list(c.GetModelDoc2.GetBodies2(0,True))[0]
    cp=pb.Copy2
    cp=pb.Copy2(False) if callable(cp) else cp
    cp.ApplyTransform(c.Transform2)
    return cp
b=body("v1_RangeHub-1"); print([round(x*1000,1) for x in b.GetBodyBox()])
def vol(b):
    return None
pairs=[("v1_RangeHub-1","v1_LockHub-1"),("v1_RangeHub-1","v1_RangeHub-1"),("v1_RangeHub-1","v1_CD_SideF-2"),("v1_RangeHub-1","v1_ModeHub-1"),("v1_ModeHub-1","v1_CD_SideF-2"),("v1_RangeHub-1","v1_Sprocket_Drive-1"),("v1_RangeHub-1","Dog_m1.25_N20-1"),("v1_ModeHub-1","v1_Sprocket_Drive-1"),("v1_ModeHub-1","Dog_m1.25_N20-1"),("v1_RangeHub-1","v1_CD_Carrier-1"),("v1_RangeHub-1","v1_CD_Spider-1"),("v1_RangeHub-1","v1_CD_Spider-2"),("v1_RangeHub-1","v1_CD_Side-1"),("v1_InDog-1","v1_LoDog-1"),("v1_InDog-1","Gear_m1.25_N29-1"),("v1_InDog-1","v1_RangeSleeve-1"),("v1_InDog-1","v1_TransferCase_Carrier_Carrier-1"),("v1_LockHub-1","v1_LockDog-1"),("v1_LockHub-1","v1_CD_Side-1"),("v1_LockHub-1","v1_LockCollar-1"),("v1_LockHub-1","v1_CD_Carrier-1"),("v1_InDog-1","25d-metal-gearmotor-75-99-1"),("v1_Sprocket_Front-3","v1_FD_Pinion-1")]
for a,b2 in pairs:
    try:
        ba=body(a); bb=body(b2)
        if ba is None or bb is None: print(a,b2,"no body", ba is None, bb is None); continue
        ca=ba; cb=bb
        from win32com.client import VARIANT
        err=swcom._out_long()
        res=ca.Operations2(2,cb,0)
        n=0;v=0
        errc=None
        if isinstance(res,tuple) and len(res)==2 and not hasattr(res[0],'GetBodyBox') and (res[0] is None or isinstance(res[0],tuple)):
            res,errc=res
        if res:
            for r_ in res:
                n+=1
                from win32com.client import dynamic
                rr=dynamic.Dispatch(r_)
                mp=rr.GetMassProperties(1.0); v+=mp[3]
        print(f"{a:34} x {b2:34} -> pieces {n} vol {v*1e9:.3f} mm3 err {errc}")
    except Exception as e:
        import traceback; traceback.print_exc(); continue
