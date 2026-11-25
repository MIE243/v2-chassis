r"""Compare two xf_<tag>.json records (argv[1], argv[2] = tags): max abs difference per component per configuration."""
import json, sys, os
H = os.path.dirname(os.path.abspath(__file__))
a, b = (json.load(open(os.path.join(H, f"xf_{t}.json"))) for t in sys.argv[1:3])
worst = 0.0
for k in a["cfg"]:
    for n in a["cfg"][k]:
        d = max(abs(x - y) for x, y in zip(a["cfg"][k][n], b["cfg"][k][n]))
        worst = max(worst, d)
        if d > 1e-9: print(f"  [{k}] {n}: max diff {d:.3e}")
print(f"{sys.argv[1]} vs {sys.argv[2]}: worst {worst:.3e}", "IDENTICAL (1e-9)" if worst <= 1e-9 else "DIFFERENT")
