import sys, os
sys.path.insert(0, sys.argv[1])
from gear_generator import swcom
pid, folder = int(sys.argv[2]), os.path.normcase(sys.argv[3])
c = [x for x in swcom.find_candidates() if x.pid == pid][0]
def docs():
    out, d = [], swcom.call(c.app, "GetFirstDocument")
    while d is not None:
        out.append((str(swcom.call(d, "GetTitle")), str(swcom.call(d, "GetPathName") or ""), int(swcom.call(d, "GetType"))))
        d = swcom.call(d, "GetNext")
    return out
before = docs()
print("open before:", before)
for kind in (2, 1):
    for title, path, k in before:
        if k == kind and path and os.path.normcase(path).startswith(folder + os.sep):
            swcom.call(c.app, "QuitDoc", title)
            print("closed without saving:", title)
print("open after:", docs())
