r"""Read-only: list swconst.tlb enum names matching argv[1] (substring) with their values."""
import sys, pythoncom
tlb = pythoncom.LoadTypeLib(r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS (2)\swconst.tlb")
for i in range(tlb.GetTypeInfoCount()):
    name = tlb.GetDocumentation(i)[0]
    if sys.argv[1].lower() in name.lower():
        ti = tlb.GetTypeInfo(i); ta = ti.GetTypeAttr()
        print(name, [(ti.GetNames(ti.GetVarDesc(j).memid)[0], ti.GetVarDesc(j).value) for j in range(ta.cVars)])
