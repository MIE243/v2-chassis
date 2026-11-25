r"""Shared helpers for the v1-centrelock scripts (imported, not run)."""
import math, os, sys
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC); sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import pythoncom
from win32com.client import VARIANT
from win32com.client import dynamic as _dynamic
from gear_generator import swcom
from gear_generator.swcom import call, _put_indexed
pythoncom.CoInitialize()
app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
M = 1000.0
R = r"C:\Users\M0obo\OneDrive\Desktop\MIE243\v1-chassis"
DF = os.path.join(R, "Differentials")
CDU = os.path.join(DF, "v1_CenterDiff_Assem.SLDASM")
CHASSIS = os.path.join(R, "v1 Chassis Assembly.SLDASM")
out = lambda: swcom._out_long()  # noqa: E731
P20 = 2 * math.pi / 20


def open_docs():
    res = []
    d = app.GetFirstDocument
    while d is not None:
        res.append((d.GetPathName, bool(d.GetSaveFlag)))
        d = d.GetNext
    return res


def comps(asm):
    return {c.Name2: c for c in asm.GetComponents(True) or ()}


def mates(asm):
    res = {}
    f = asm.FirstFeature
    while f is not None:
        if f.GetTypeName2 == "MateGroup":
            s = f.GetFirstSubFeature
            while s is not None:
                res[s.Name] = s
                s = s.GetNextSubFeature
        f = f.GetNextFeature
    return res


def errors(asm):
    bad = []
    for n, s in mates(asm).items():
        w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
        code = s.GetErrorCode2(w)
        if code or w.value:
            bad.append((n, code, w.value))
    return bad


def xf(c):
    return [float(v) for v in c.Transform2.ArrayData]


def origin(c):
    a = xf(c)
    return tuple(round(v * M, 4) for v in a[9:12])


def zaxis(c):
    return [round(v, 6) for v in xf(c)[6:9]]


def ang(c):
    a = xf(c)
    return math.atan2(a[1], a[0])


def wrap(x, p=P20):
    x = x % p
    return x - p if x > p / 2 else x


def put_xf(c, data):
    util = call(app, "GetMathUtility"); ole = util._oleobj_
    raw = ole.Invoke(ole.GetIDsOfNames("CreateTransform"), 0, pythoncom.DISPATCH_METHOD, True,
                     VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, data))
    swcom._put(c, "Transform2", raw if hasattr(raw, "ArrayData") else _dynamic.Dispatch(raw))


def put_rot(c, theta, z):
    put_xf(c, [math.cos(theta), math.sin(theta), 0.0, -math.sin(theta), math.cos(theta), 0.0, 0.0, 0.0, 1.0,
               0.0, 0.0, z / M, 1.0, 0.0, 0.0, 0.0])


def mate_desc(asm, s, cfgs):
    m = s.GetSpecificFeature2
    ents = []
    try:
        for i in range(m.GetMateEntityCount):
            e = m.MateEntity(i); c = e.ReferenceComponent
            ents.append((c.Name2 if c else "asm", e.ReferenceType2))
    except Exception as ex:  # noqa: BLE001
        ents = str(ex)
    w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
    code = s.GetErrorCode2(w)
    vals = None
    dd = s.GetFirstDisplayDimension
    if dd is not None:
        vals = [round(v * M, 4) for v in dd.GetDimension2(0).GetSystemValue3(2, cfgs)]
    extra = ""
    try:
        g = s.GetDefinition
        extra = f"ratio {g.GearRatioNumerator}:{g.GearRatioDenominator} reverse {g.Reverse}"
    except Exception:  # noqa: BLE001
        pass
    try: t = m.Type; fl = m.Flipped; al = m.Alignment
    except Exception: t = fl = al = "?"  # noqa: E701
    return (f"{s.Name:34} type {t} align {al} flipped {fl} ents {ents} vals {vals} "
            f"supp {list(s.IsSuppressed2(2, cfgs))} err {code},{w.value} {extra}")


OPTS = (("TreatCoincidenceAsInterference", False), ("TreatSubAssembliesAsComponents", False),
        ("IncludeMultibodyPartInterferences", True), ("MakeInterferingPartsTransparent", False),
        ("CreateFastenersFolder", False), ("IgnoreHiddenBodies", True), ("ShowIgnoredInterferences", False),
        ("UseTransform", False))


def interferences(asm):
    mgr = call(asm, "InterferenceDetectionManager")
    for n, v in OPTS: setattr(mgr, n, v)  # noqa: E701
    hits = []
    try:
        items = mgr.GetInterferences
        items = items() if type(items).__name__ == "method" else items
        for it in items or ():
            cn = sorted(str(x.Name2) for x in (it.Components or ()))
            hits.append((round(float(it.Volume) * 1e9, 3), cn))
    finally:
        mgr.Done()
    return hits


def vol(doc):
    mp = call(call(doc, "Extension"), "CreateMassProperty")
    mp = mp() if type(mp).__name__ == "method" else mp
    return float(mp.Volume) * 1e9
