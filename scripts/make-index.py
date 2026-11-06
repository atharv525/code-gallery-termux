#!/usr/bin/env python3
"""Write packages.json (name, version, arch, description) for the site."""
import json, sys
src = sys.argv[1]
pkgs, cur = {}, {}
for line in open(src).read().split("\n") + [""]:
    if not line.strip():
        if cur: pkgs[cur["Package"]] = cur
        cur = {}
    elif not line.startswith(" ") and ":" in line:
        k, v = line.split(":", 1); cur[k] = v.strip()
print(json.dumps([{k: p.get(k, "") for k in ("Package", "Version", "Architecture", "Description")}
                  for p in sorted(pkgs.values(), key=lambda p: p["Package"])], indent=1))
