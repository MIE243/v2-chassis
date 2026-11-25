r"""One plain Build of a workbook through the Workbook window, as its Build button does, on the SolidWorks session
given by PID; nothing doctored. python.exe v1_build.py <src> <pid> <workbook> <log> <appdata>

The build's result and plan are observed (swbuild.build_gearbox and plan_gearbox wrapped to keep what they return,
changing nothing). Any SolidWorks dialog is logged, never answered. Ends with the window closed and the strip gone;
SolidWorks is left as the build left it."""
import json, os, sys, threading, time, traceback
SRC, PID, BOOK, LOG, APPDATA = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
os.environ["APPDATA"] = APPDATA
sys.path.insert(0, SRC)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import tkinter as tk  # noqa: E402
import pythoncom  # noqa: E402
import win32gui, win32process  # noqa: E402
from gear_generator import gui, swbuild, swcom, theme, workbook_gui  # noqa: E402
from gear_generator.swcom import call  # noqa: E402

open(LOG, "w", encoding="utf-8").close()


def log(kind, **kw):
    text = time.strftime("%H:%M:%S") + " " + kind + " " + json.dumps(kw, ensure_ascii=False, default=str)
    print(text, flush=True)
    with open(LOG, "a", encoding="utf-8") as h:
        h.write(text + "\n")


NOTIFY = ("Title", "Description", "Button1", "Button2", "Hyperlink Text 1", "Hyperlink Text 2")
STOP = threading.Event()


def texts_of(hwnd):
    out = []
    win32gui.EnumChildWindows(hwnd, lambda c, _: out.append(win32gui.GetWindowText(c)) or True, None)
    return [t for t in out if t]


def watch():
    seen = set()
    while not STOP.is_set():
        found = []

        def each(h, _):
            if win32gui.IsWindowVisible(h) and win32process.GetWindowThreadProcessId(h)[1] == PID \
                    and win32gui.GetClassName(h) in ("#32770", "swBalloonTip"):
                found.append(h)
            return True
        try:
            win32gui.EnumWindows(each, None)
        except Exception:  # noqa: BLE001
            pass
        for h in found:
            try:
                key = (h, win32gui.GetWindowText(h), tuple(texts_of(h)[:8]))
            except Exception:  # noqa: BLE001
                continue
            ticking = any(t.startswith("Elapsed time") for t in key[2])
            if (h if ticking else key) in seen:
                continue
            seen.add(h if ticking else key)
            kind = "notification box (exempt)" if key[2][:6] == NOTIFY else win32gui.GetClassName(h)
            log("DIALOG", kind=kind, title=key[1], texts=list(key[2]), now=CALL["now"])
        time.sleep(1)


CALL = {"now": ""}
_raw = swcom.call


def traced(obj, name, *args):
    before, CALL["now"] = CALL["now"], name
    try:
        return _raw(obj, name, *args)
    finally:
        CALL["now"] = before


swcom.call = traced
KEPT = {}
_build = swbuild.build_gearbox


def build_gearbox(*a, **k):
    started = time.monotonic()
    result = _build(*a, **k)
    KEPT["result"], KEPT["seconds"] = result, time.monotonic() - started
    return result


swbuild.build_gearbox = build_gearbox
_plan = workbook_gui.wb_gearbox.plan_gearbox


def plan_gearbox(*a, **k):
    plan = _plan(*a, **k)
    KEPT["plan"] = plan
    return plan


workbook_gui.wb_gearbox.plan_gearbox = plan_gearbox


def asked(parent, title, question):
    log("ASKED (answered No)", title=title, question=question)
    return False


workbook_gui.ask_yes_no = asked

threading.Thread(target=watch, daemon=True).start()
pythoncom.CoInitialize()
newest = swcom.choose(swcom.find_candidates())
log("attach", newest=newest.pid, revision=newest.revision, wanted=PID)
if newest.pid != PID:
    log("STOP", why="the strip would attach to another SolidWorks")
    raise SystemExit(2)
gui._declare_dpi_aware()
theme.register_bundled_fonts()
root = tk.Tk()
root.title("GG v1 build")
app = gui.GearApp(root, scale=gui._scale_to_dpi(root))
root.withdraw()
if len(sys.argv) > 6:
    app.out_folder.set(sys.argv[6])           # the strip's Output folder, for this run only (APPDATA is a copy)
log("strip", output_folder=app.out_folder.get(), part_template=app.part_template.get())
win = workbook_gui.open_workbook(app, BOOK)
win.title("GG v1 build workbook")
T0 = time.time()
STATE = {"phase": "read", "pressed": 0.0}


def idle():
    return win._pending is None and win._job is None  # noqa: SLF001


def finish(code):
    STATE["code"] = code
    try:
        win.close()
    except Exception:  # noqa: BLE001
        pass
    root.after(500, root.destroy)


def step():
    try:
        if STATE["phase"] == "read":
            if win.reading is not None and idle():
                f = win.footer()
                spec = win.reading.spec
                log("read", ok=win.reading.ok, error=win.reading.error, status=win.status.get(),
                    folder=win._folder(spec), build=(f.build_label, f.build_enabled))  # noqa: SLF001
                if not (win.reading.ok and f.build_enabled):
                    log("REFUSED before the build", status=win.status.get())
                    return finish(3)
                STATE["phase"], STATE["pressed"] = "build", time.time()
                log("press", what="Build")
                win.build_button.command()
            elif time.time() - T0 > 120:
                log("TIMEOUT", what="the read")
                return finish(4)
        elif STATE["phase"] == "build":
            if idle() and time.time() - STATE["pressed"] > 3:
                res, plan = KEPT.get("result"), KEPT.get("plan")
                log("status", text=win.status.get(), seconds=round(time.time() - STATE["pressed"], 1))
                if res is not None:
                    log("result", ok=res.ok, result_kind=res.kind, seconds=round(KEPT["seconds"], 1),
                        lines=list(res.log_lines()))
                    asm = res.assembly
                    if asm is not None:
                        log("assembly", document=asm.document, saved=asm.saved, mate_problems=list(asm.mate_problems),
                            failures=[list(f) for f in asm.failures], turned_round=list(getattr(asm, "turned_round", [])),
                            clashes=[(c.gears, c.volume) for c in (getattr(res, "clashes", None) or [])])
                if plan is not None:
                    ops = []
                    if plan.assembly is not None:
                        ops += [(op.name, op.flip) for op in plan.assembly.ops if getattr(op, "kind", "") == "gear"]
                    if plan.modes_plan is not None:
                        ops += [(op.name, op.flip, s.name) for s in plan.modes_plan.steps for op in s.ops]
                    log("planned gear mates (name, Flip as first made[, mode])", ops=ops,
                        assembly=plan.assembly_path, layout=plan.layout_path)
                return finish(0)
            if time.time() - STATE["pressed"] > 3000:
                log("TIMEOUT", what="the build", status=win.status.get())
                return finish(5)
        root.after(1000, step)
    except Exception:  # noqa: BLE001
        log("SCRIPT FAULT", error=traceback.format_exc())
        finish(6)


root.report_callback_exception = lambda e, v, tb: (log("CALLBACK FAILED", error="".join(
    traceback.format_exception(e, v, tb))), finish(7))
root.after(1000, step)
root.mainloop()
STOP.set()
log("done", code=STATE.get("code"))
os._exit(STATE.get("code", 1) or 0)
