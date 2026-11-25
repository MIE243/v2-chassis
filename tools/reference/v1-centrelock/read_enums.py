r"""Read-only: dump enums from SolidWorks 2024 swconst.tlb."""
import sys, pythoncom
want = set(sys.argv[1:])
tlb = pythoncom.LoadTypeLib(r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS (2)\swconst.tlb")
for i in range(tlb.GetTypeInfoCount()):
    name = tlb.GetDocumentation(i)[0]
    if name in want:
        ti = tlb.GetTypeInfo(i); ta = ti.GetTypeAttr()
        vals = []
        for j in range(ta.cVars):
            vd = ti.GetVarDesc(j); vals.append((ti.GetNames(vd.memid)[0], vd.value))
        print(name, vals)
