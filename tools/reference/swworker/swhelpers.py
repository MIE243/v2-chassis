"""Helpers available inside worker jobs. Reloadable with `sw.py reload`."""
import contextlib
import pythoncom
from win32com.client import VARIANT
from gear_generator import swcom

app = None   # bound by worker (re-bound after every re-attach)


def bind(a):
    global app
    app = a


def doc(path_or_title):
    """Open document by full path or title (never opens a second copy of an already open one)."""
    d = app.GetOpenDocumentByName(path_or_title)
    if d is not None:
        return d
    for d in _open_docs():
        if d.GetTitle == path_or_title or d.GetTitle.rsplit('.', 1)[0] == path_or_title \
                or d.GetPathName.lower() == str(path_or_title).lower():
            return d
    import os
    ext = os.path.splitext(path_or_title)[1].lower()
    if not os.path.isabs(path_or_title):
        raise ValueError("not open and not a full path: %r" % path_or_title)
    t = {'.sldprt': 1, '.sldasm': 2, '.slddrw': 3}[ext]
    err, warn = swcom._out_long(), swcom._out_long()
    d = app.OpenDoc6(path_or_title, t, 1 | 0, "", err, warn)   # silent
    if d is None:
        raise RuntimeError("OpenDoc6 failed, error %s" % err.value)
    return d


def _open_docs():
    d = app.GetFirstDocument
    while d is not None:
        yield d
        d = d.GetNext


def comps(asm, top=True):
    """{Name2: component}. top=True -> top-level only, False -> all levels."""
    return {c.Name2: c for c in (asm.GetComponents(top) or ())}


def _mate_group(doc_):
    f = doc_.FirstFeature
    while f is not None:
        if f.GetTypeName2 == "MateGroup":
            return f
        f = f.GetNextFeature
    return None


def mate_errors(asm):
    """[(mate name, error code, is_warning)] for mates with a nonzero error code."""
    out = []
    g = _mate_group(asm)
    if g is None:
        return out
    s = g.GetFirstSubFeature
    while s is not None:
        w = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
        code = s.GetErrorCode2(w)
        if code:
            out.append((s.Name, code, bool(w.value)))
        s = s.GetNextSubFeature
    return out


def whats_wrong(d):
    """[(feature name, type name, code, is_warning)] from Extension.GetWhatsWrong."""
    ext = d.Extension
    if not ext.GetWhatsWrongCount:
        return []
    feats = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)
    codes = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)
    warns = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)
    ext.GetWhatsWrong(feats, codes, warns)
    out = []
    cs, ws = list(codes.value or ()), list(warns.value or ())
    for i, f in enumerate(feats.value or ()):
        try:
            n, t = f.Name, f.GetTypeName2
        except Exception:
            n, t = "?", "?"
        out.append((n, t, cs[i] if i < len(cs) else None, bool(ws[i]) if i < len(ws) else None))
    return out


def xf(comp):
    """12 floats: ArrayData rotation (9, SolidWorks order) + translation in mm."""
    a = list(comp.Transform2.ArrayData)
    return [round(v, 9) for v in a[:9]] + [round(v * 1000, 6) for v in a[9:12]]


@contextlib.contextmanager
def batch(d):
    """EDIT jobs: CommandInProgress + graphics/feature-tree updates off; restores exact previous
    values on exit (even on error) and does ONE EditRebuild3. Usage: with batch(doc): ..."""
    saved = []   # (obj, prop, old)

    def setp(obj, prop, val):
        try:
            old = getattr(obj, prop)
        except Exception:
            return
        try:
            setattr(obj, prop, val)
            saved.append((obj, prop, old))
        except Exception:
            pass

    mv = d.ActiveView
    fm = d.FeatureManager
    setp(app, "CommandInProgress", True)
    if mv is not None:
        setp(mv, "EnableGraphicsUpdate", False)
    setp(fm, "EnableFeatureTreeWindow", False)
    setp(fm, "EnableFeatureTree", False)
    try:
        yield d
    finally:
        for obj, prop, old in reversed(saved):
            try:
                setattr(obj, prop, old)
            except Exception:
                pass
        d.EditRebuild3
