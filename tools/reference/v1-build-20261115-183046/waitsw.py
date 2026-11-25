import sys, time
sys.path.insert(0, sys.argv[1])
from gear_generator import swcom
pid = int(sys.argv[2])
for i in range(90):
    try:
        found = [c for c in swcom.find_candidates() if c.pid == pid]
        if found:
            print("reachable", found[0].revision, "after", i * 5, "s"); break
    except Exception as exc:
        print("not yet", type(exc).__name__, exc)
    time.sleep(5)
else:
    print("never reachable")
