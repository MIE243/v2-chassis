r"""After the plain Build: the app's own reads of what it built, an interference read at four turns of the input in the
first mode (the driven proofs' angle-mate drive, made where the input stands, deleted after, the train back where it
was), the documents saved, the first mode shown, zoomed to fit, the assembly active; SolidWorks left open.
python.exe v1_post.py <src> <pid> <workbook> <log>"""
import json, math, os, sys, time, traceback
SRC, PID, BOOK, LOG = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
sys.path.insert(0, SRC)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from gear_generator import store, swbuild, swcom  # noqa: E402
from gear_generator.swcom import call  # noqa: E402
from gear_generator.workbook import geometry as wb_geometry  # noqa: E402


def log(kind, **kw):
    text = time.strftime("%H:%M:%S") + " " + kind + " " + json.dumps(kw, ensure_ascii=False, default=str)
    print(text, flush=True)
    with open(LOG, "a", encoding="utf-8") as h:
        h.write(text + "\n")


rec = store.read_link_record(BOOK)
box = rec.gearbox
c = [x for x in swcom.find_candidates() if x.pid == PID][0]
s = swcom.Session(c.app, c.revision, c.pid)
pairs = [(x.gear, x.name) for x in box.components] + [(cc.shaft + " carrier", cc.component)
                                                       for cc in getattr(box, "carriers", [])]
gear_of = {n: g for g, n in pairs}
log("record", assembly=box.assembly, layout=box.layout, box_kind=box.kind, modes=list(box.modes), drag=list(box.drag),
    parts=[e.path for e in rec.parts], carriers=[cc.path for cc in getattr(box, "carriers", [])])


def frames(prefix):
    out = {}
    for i, (g, n) in enumerate(pairs):
        s.find_component(f"{prefix}{i}", n)
        out[g] = s.component_frame(f"{prefix}{i}")
    return out


def gap(a, b):
    return max(max(abs(float(x) - float(y)) for x, y in zip(a[g][0], b[g][0])) +
               max(abs(float(x) - float(y)) for x, y in zip(a[g][1], b[g][1])) for g in a)


s.begin_build()
try:
    s.open_document(box.assembly)
    log("open", active=s.active_configuration(), configurations=s.configurations())
    modes = list(box.modes)
    slides = [m.name for m in box.mates if m.kind == "slide"]
    couples = [m.name for m in box.mates if m.kind == "couple"]
    vals, flags = {}, {}
    for i, n in enumerate(slides):
        s.find_mate(f"sl{i}", n)
        vals[n] = s.dimension_values(f"sl{i}", modes)
    for i, n in enumerate(couples):
        s.find_mate(f"cp{i}", n)
        flags[n] = {m: ("off" if f else "on") for m, f in s.mate_suppression(f"cp{i}", modes).items()}
    log("per mode: slide values (mm)", values=vals)
    log("per mode: couplings", couplings=flags)
    states = [(m.name, m.code, m.warning, m.suppressed) for m in s.mate_states()]
    log("mates as read in the active configuration (name, code, warning, suppressed)", mates=states)
    # The interference read at four turns of the input in the first mode.
    first, sun = modes[0], box.drag[0]
    s.show_configuration(first)
    s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
    sun_name = dict(pairs)[sun]
    placed_axis = (0.0, 0.0, 1.0)
    before = frames("b")
    rot = before[sun][0]
    axis = (float(rot[2]), float(rot[5]), float(rot[8]))
    base = wb_geometry.base_frame(axis)
    u0 = (float(base[0]), float(base[3]), float(base[6]))
    plane = (("plane3", "plane2", "plane1"))[max(range(3), key=lambda i: abs(u0[i]))]
    theta = swbuild.turn_between(base, rot)
    theta = 0.0 if theta is None else math.degrees(theta)
    from gear_generator.workbook import link as wb_link
    spec = wb_link.Link(BOOK).read().spec
    teeth = next((int(float(g.teeth)) for g in spec.gears if g.id == sun), 0)
    log("drive", mode=s.active_configuration(), input=sun, axis=axis, plane=plane, input_at=theta, teeth=teeth)
    s.find_component("dsun", sun_name)
    s.find_component("dlay", box.layout_component)
    at = 90.0 + theta
    name, dim = s.add_mate("ddrive", "angle", "dsun:plane2", f"dlay:{plane}", at, "GG check drive")
    s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
    made = frames("m")
    log("drive made", name=name, status=s.mate_status(name), moved=gap(made, before))
    pitch = 360.0 / teeth if teeth else 360.0 / 29
    reads = []
    try:
        for k in range(4):
            turn = k * pitch / 4
            s.set_dimension_in("ddrive", math.radians(at + turn) * 1000.0, [first])
            s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
            now = frames(f"t{k}")
            got = swbuild.turn_between(before[sun][0], now[sun][0])
            clashes = [(cl.gears, round(cl.volume, 3)) for cl in swbuild._clashes(s.interferences(), gear_of)]  # noqa: SLF001
            reads.append((round(turn, 3), None if got is None else round(math.degrees(got), 6), clashes))
            log("interference", sun_turn=round(turn, 3), sun_read=None if got is None else round(math.degrees(got), 6),
                clashes=clashes)
    finally:
        s.set_dimension_in("ddrive", math.radians(at) * 1000.0, [first])
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        feature = s._mate_feature(name)  # noqa: SLF001
        doc = s._doc()  # noqa: SLF001
        call(doc, "ClearSelection2", True)
        call(feature, "Select2", False, 0)
        swcom._guarded("EditDelete", lambda: doc.EditDelete())  # noqa: SLF001
        call(doc, "ClearSelection2", True)
        s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
        after = frames("a")
        log("drive deleted, the train back", gone=name not in s._mate_names(), off_from_before=gap(after, before))  # noqa: SLF001
    # Save what is modified among the build's documents.
    paths = [box.assembly, box.layout] + [e.path for e in rec.parts] + [cc.path for cc in getattr(box, "carriers", [])]
    saved = []
    d = call(c.app, "GetFirstDocument")
    docs = []
    while d is not None:
        docs.append(d)
        d = call(d, "GetNext")
    for d in docs:
        p = str(call(d, "GetPathName") or "")
        if any(store.same_path(p, q) for q in paths) and call(d, "GetSaveFlag"):
            ok = call(call(d, "Extension"), "SaveAs3", p, 0, 1, swcom._null_dispatch(), swcom._null_dispatch(),  # noqa: SLF001
                      swcom._out_long(), swcom._out_long())  # noqa: SLF001
            saved.append((os.path.basename(p), bool(ok)))
    log("saved (modified ones only)", saved=saved)
    s.show_configuration(first)
    s.rebuild(kind=swcom.ASSEMBLY_TRAIN)
    asm_doc = s._doc()  # noqa: SLF001
    title = str(call(asm_doc, "GetTitle"))
    errs = swcom._out_long()  # noqa: SLF001
    call(c.app, "ActivateDoc3", title, False, 0, errs)
    call(asm_doc, "ViewZoomtofit2")
    left = []
    d = call(c.app, "GetFirstDocument")
    while d is not None:
        left.append((str(call(d, "GetTitle")), bool(call(d, "GetSaveFlag"))))
        d = call(d, "GetNext")
    log("left open", active=s.active_configuration(), title=title, documents=left)
except Exception:  # noqa: BLE001
    log("FAULT", error=traceback.format_exc())
finally:
    s.end_build()
log("done")
