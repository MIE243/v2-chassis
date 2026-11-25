# swworker: persistent SolidWorks COM worker

Transport: file queue (jobs/<id>.json -> results/<id>.json, polled every 30 ms). WSL cannot reach Windows
127.0.0.1 (NAT mode) and the Windows firewall blocks the WSL gateway IP, so TCP was rejected. Round trip ~0.1 s.

    python3 /mnt/c/Users/M0obo/Documents/GearGeneratorProbe/swworker/sw.py start|stop|ping|status|reload
    sw.py run file.py | run -c "code" [--timeout N] [--json]   # prints stdout; exit 1 on job error (traceback on stderr)
    sw.py stop --force     # taskkill, if a job hangs (client timeout does not interrupt a running job)

`start` launches hidden via PowerShell Start-Process (no console, no dialog) with defaults src/pid 84260;
edit PID/SRC at top of sw.py if SolidWorks restarts. Status: swworker/status.json (pid, heartbeat, busy).
Jobs run on the worker's one COM thread, in a persistent namespace (`result = ...` is returned as JSON).
Worker re-attaches automatically if COM breaks. After editing swhelpers.py run `sw.py reload`.

Namespace: app swcom pythoncom VARIANT os math json + helpers:
- doc(path_or_title); comps(asm, top=True) -> {Name2: comp}
- mate_errors(asm) -> [(name, code, is_warning)]; whats_wrong(doc) -> [(name, type, code, is_warning)]
- xf(comp) -> 12 floats (Transform2.ArrayData rotation 9, translation mm)
- batch(doc): context manager for EDITS

Batch rule: all edits inside `with batch(doc):`; one rebuild per batch (done on exit); run interference
checks only on configurations that changed. batch sets CommandInProgress, EnableGraphicsUpdate (ModelView),
EnableFeatureTree/EnableFeatureTreeWindow (FeatureManager) off, restores previous values in finally.

Late-binding rules: zero-arg members run on attribute access (`doc.GetSaveFlag`, `asm.EditRebuild3`);
arg-less methods returning nothing/arrays must be called (`asm.EditDelete()`, `mgr.Done()`,
`face.GetTessTriangles(True)`); GetErrorCode2 needs VARIANT(VT_BYREF|VT_BOOL, False).
Keep every SolidWorks call on the job thread; never return COM objects, only plain data.
