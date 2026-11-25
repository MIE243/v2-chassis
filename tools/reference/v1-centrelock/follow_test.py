r"""Follow test: D1@LAYOUT 141.5 -> 131.5, read all origins in Default and Locked (must all move +10 in Z, lock gaps kept),
then restore 141.5 and re-read. Ends on Default with D1 = 141.5. Saves nothing."""
from lockcommon import *  # noqa: F401,F403
asm = app.GetOpenDocumentByName(CDU)
car = app.GetOpenDocumentByName(os.path.join(DF, "v1_CD_Carrier.SLDPRT"))
dim = car.Parameter("D1@LAYOUT")


def read(tag):
    res = {}
    for k in ("Default", "Locked"):
        asm.ShowConfiguration2(k); asm.EditRebuild3
        res[k] = {n: origin(c)[2] for n, c in comps(asm).items()}
        print(f"  [{tag} / {k}] errors {errors(asm) or 'none'} | Z {res[k]}")
    asm.ShowConfiguration2("Default"); asm.EditRebuild3
    return res


def set_d1(v):
    dim.SetSystemValue3(v / M, 1, None); car.EditRebuild3
    app.ActivateDoc3(asm.GetTitle, False, 0, out()); asm.EditRebuild3
    print(f"D1 = {dim.SystemValue * M:.3f}")


app.ActivateDoc3(asm.GetTitle, False, 0, out())
a = read("141.5")
set_d1(131.5); b = read("131.5")
moves = {k: {n: round(b[k][n] - a[k][n], 4) for n in a[k]} for k in a}
print("moves:", moves)
set_d1(141.5); c = read("restored")
print("restored equals original:", c == a)
