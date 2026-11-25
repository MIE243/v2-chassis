#!/usr/bin/env python3
"""WSL client for the SolidWorks worker. See README.md."""
import sys, os, json, time, uuid, subprocess, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
WINHERE = r"C:\Users\M0obo\Documents\GearGeneratorProbe\swworker"
SRC = r"C:\Users\M0obo\Documents\GearGeneratorProbe\v1-build-20261115-183046\snap\src"
PID = 84260
JOBS, RESULTS, STATUS = (os.path.join(HERE, x) for x in ("jobs", "results", "status.json"))


def status():
    try:
        with open(STATUS) as f:
            s = json.load(f)
    except Exception:
        return None
    return s


def worker_up():
    s = status()
    return bool(s) and time.time() - s.get("heartbeat", 0) < 6 and not (False)


def submit(job, timeout):
    os.makedirs(JOBS, exist_ok=True); os.makedirs(RESULTS, exist_ok=True)
    jid = "%d-%s" % (time.time() * 1000, uuid.uuid4().hex[:6])
    tmp = os.path.join(JOBS, jid + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(job, f)
    os.replace(tmp, os.path.join(JOBS, jid + ".json"))
    rp = os.path.join(RESULTS, jid + ".json")
    end = time.time() + timeout
    while time.time() < end:
        if os.path.exists(rp):
            try:
                with open(rp, encoding="utf-8") as f:
                    r = json.load(f)
            except Exception:
                time.sleep(0.01); continue
            os.remove(rp)
            return r
        time.sleep(0.01)
    try:
        os.remove(os.path.join(JOBS, jid + ".json")); queued = True
    except OSError:
        queued = False
    return {"ok": False, "stdout": "", "error": "client timeout after %ss (%s). Worker may still be running the job; "
            "use `sw.py stop --force` then `sw.py start` if it hangs." % (timeout, "job never started, withdrawn" if queued else "job was running")}


def emit(r, as_json=False):
    if as_json:
        print(json.dumps(r)); return 0 if r.get("ok") else 1
    sys.stdout.write(r.get("stdout", ""))
    if r.get("result") is not None:
        print("result =", json.dumps(r["result"]) if not isinstance(r["result"], str) else r["result"])
    if not r.get("ok"):
        sys.stderr.write(r.get("error", "error") + "\n"); return 1
    if os.environ.get("SW_TIME"):
        sys.stderr.write("[%.3fs]\n" % r.get("elapsed", 0))
    return 0


def start():
    if worker_up():
        print("already running:", json.dumps(status())); return 0
    try: os.remove(STATUS)
    except OSError: pass
    ps = ("Start-Process -FilePath python.exe -ArgumentList 'worker.py','%s','%d' "
          "-WorkingDirectory '%s' -WindowStyle Hidden" % (SRC, PID, WINHERE))
    subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    for _ in range(300):
        time.sleep(0.1)
        if worker_up():
            print("started:", json.dumps(status())); return 0
    print("worker did not come up (run `python.exe worker.py <src> <pid>` in a console to see why)"); return 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("file", nargs="?"); r.add_argument("-c", dest="code")
    r.add_argument("--timeout", type=float, default=120); r.add_argument("--json", action="store_true")
    for n in ("ping", "start", "reload", "status"):
        sub.add_parser(n)
    s = sub.add_parser("stop"); s.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if a.cmd == "start": return start()
    if a.cmd == "status":
        print(json.dumps(status()) if status() else "no status file"); return 0
    if a.cmd == "stop":
        st = status()
        if not st: print("not running"); return 0
        if a.force:
            subprocess.run(["taskkill.exe", "/F", "/PID", str(st["pid"])], stdout=subprocess.DEVNULL)
            try: os.remove(STATUS)
            except OSError: pass
            print("killed"); return 0
        r = submit({"kind": "shutdown"}, 15)
        print("stopped" if r["ok"] else r["error"]); return 0 if r["ok"] else 1
    if not worker_up():
        print("worker not running; `sw.py start`", file=sys.stderr); return 2
    if a.cmd in ("ping", "reload"):
        r = submit({"kind": a.cmd}, 10); print(json.dumps(r.get("result")) if r["ok"] else r["error"]); return 0 if r["ok"] else 1
    if a.code is not None: code, name = a.code, "<-c>"
    elif a.file:
        with open(a.file, encoding="utf-8") as f: code = f.read()
        name = os.path.abspath(a.file)
    else: code, name = sys.stdin.read(), "<stdin>"
    return emit(submit({"kind": "run", "code": code, "name": name}, a.timeout), a.json)


sys.exit(main())
