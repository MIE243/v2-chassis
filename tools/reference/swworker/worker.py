"""Persistent SolidWorks worker (Windows Python). Usage: python worker.py <src> <pid>
File-queue transport (see README): jobs/<id>.json -> results/<id>.json."""
import sys, os, io, json, time, traceback, importlib, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SRC, PID = sys.argv[1], int(sys.argv[2])
sys.path.insert(0, SRC)
import pythoncom
from win32com.client import VARIANT
from gear_generator import swcom
import swhelpers

JOBS, RESULTS = os.path.join(HERE, "jobs"), os.path.join(HERE, "results")
STATUS = os.path.join(HERE, "status.json")
for d in (JOBS, RESULTS):
    os.makedirs(d, exist_ok=True)
pythoncom.CoInitialize()
NS = {}
state = {"pid": os.getpid(), "sw_pid": PID, "transport": "file-queue", "started": time.time(),
         "jobs_done": 0, "busy": False, "reattaches": 0}


def write_status():
    state["heartbeat"] = time.time()
    tmp = STATUS + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, STATUS)


def attach():
    app = [c for c in swcom.find_candidates() if c.pid == PID][0].app
    NS.update(app=app, swcom=swcom, pythoncom=pythoncom, VARIANT=VARIANT, os=os, math=math, json=json)
    swhelpers.bind(app)
    return app


def load_helpers():
    importlib.reload(swhelpers)
    swhelpers.bind(NS["app"])
    for n in dir(swhelpers):
        if not n.startswith("_") and callable(getattr(swhelpers, n)) and n not in ("bind",):
            NS[n] = getattr(swhelpers, n)
    NS["swhelpers"] = swhelpers


def alive():
    try:
        NS["app"].RevisionNumber
        return True
    except Exception:
        return False


def ensure():
    if "app" not in NS or not alive():
        attach(); state["reattaches"] += 1
        load_helpers()


def run_job(job):
    t0 = time.time()
    res = {"ok": True, "stdout": "", "result": None, "error": None}
    old = sys.stdout
    buf = io.StringIO()
    sys.stdout = buf
    try:
        kind = job.get("kind", "run")
        if kind == "ping":
            ensure()
            res["result"] = {"pid": os.getpid(), "sw_rev": NS["app"].RevisionNumber,
                             "jobs_done": state["jobs_done"], "reattaches": state["reattaches"]}
        elif kind == "reload":
            ensure(); load_helpers()
        elif kind == "shutdown":
            res["_shutdown"] = True
        else:
            ensure()
            NS.pop("result", None)
            exec(compile(job["code"], job.get("name", "<job>"), "exec"), NS)
            r = NS.get("result")
            try:
                json.dumps(r); res["result"] = r
            except Exception:
                res["result"] = repr(r)
    except BaseException:
        res["ok"] = False
        res["error"] = traceback.format_exc()
    finally:
        sys.stdout = old
    res["stdout"] = buf.getvalue()
    res["elapsed"] = round(time.time() - t0, 4)
    return res


def main():
    try:
        ensure()
    except Exception:
        print("initial attach failed:", traceback.format_exc())
    write_status()
    last = 0
    while True:
        try:
            names = sorted(n for n in os.listdir(JOBS) if n.endswith(".json"))
        except Exception:
            names = []
        for n in names:
            p = os.path.join(JOBS, n)
            try:
                with open(p, encoding="utf-8") as f:
                    job = json.load(f)
                os.remove(p)
            except Exception:
                continue
            state["busy"] = True; write_status()
            res = run_job(job)
            state["busy"] = False; state["jobs_done"] += 1
            tmp = os.path.join(RESULTS, n + ".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({k: v for k, v in res.items() if k != "_shutdown"}, f)
            os.replace(tmp, os.path.join(RESULTS, n))
            write_status()
            if res.get("_shutdown"):
                try: os.remove(STATUS)
                except OSError: pass
                return
        if time.time() - last > 2:
            write_status(); last = time.time()
        time.sleep(0.03)


main()
