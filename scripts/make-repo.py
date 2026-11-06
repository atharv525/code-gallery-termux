#!/usr/bin/env python3
"""Write dists/<suite>/main/binary-<arch>/Packages(.gz) and Release for out/.

Architecture: all packages are listed in every binary-<arch> index, the way
the official Termux repos do it."""
import gzip, hashlib, os, subprocess, sys, time
from email.utils import formatdate

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
SUITE = "codegallery"
ARCHES = ["aarch64", "arm", "i686", "x86_64"]
FIELDS = ["Package", "Version", "Architecture", "Maintainer", "Installed-Size",
          "Depends", "Recommends", "Suggests", "Conflicts", "Section", "Priority",
          "Homepage", "Description"]

def control(deb):
    return subprocess.run(["dpkg-deb", "-f", deb], check=True,
                          capture_output=True, text=True).stdout.rstrip("\n")

def digests(path):
    data = open(path, "rb").read()
    return len(data), {n: hashlib.new(n, data).hexdigest() for n in ("md5", "sha1", "sha256")}

entries = {a: [] for a in ARCHES}
for dirpath, _, files in os.walk(os.path.join(OUT, "pool")):
    for f in sorted(files):
        if not f.endswith(".deb"):
            continue
        p = os.path.join(dirpath, f)
        ctl = control(p)
        arch = next(l.split(":", 1)[1].strip() for l in ctl.splitlines() if l.startswith("Architecture:"))
        size, d = digests(p)
        rel = os.path.relpath(p, OUT)
        stanza = (f"{ctl}\nFilename: {rel}\nSize: {size}\nMD5sum: {d['md5']}\n"
                  f"SHA1: {d['sha1']}\nSHA256: {d['sha256']}\n")
        for a in (ARCHES if arch == "all" else [arch]):
            if a in entries:
                entries[a].append(stanza)

base = os.path.join(OUT, "dists", SUITE)
index_files = []
for a in ARCHES:
    d = os.path.join(base, "main", f"binary-{a}")
    os.makedirs(d, exist_ok=True)
    text = "\n".join(sorted(entries[a])).encode()
    open(os.path.join(d, "Packages"), "wb").write(text)
    with gzip.GzipFile(os.path.join(d, "Packages.gz"), "wb", mtime=0) as g:
        g.write(text)
    index_files += [f"main/binary-{a}/Packages", f"main/binary-{a}/Packages.gz"]

lines = [
    "Origin: Code Gallery", "Label: Code Gallery", f"Suite: {SUITE}", f"Codename: {SUITE}",
    f"Date: {formatdate(time.time(), usegmt=True)}",
    f"Architectures: {' '.join(ARCHES)}", "Components: main",
    "Description: Code Gallery - extra packages for Termux",
]
for title, algo in (("MD5Sum", "md5"), ("SHA1", "sha1"), ("SHA256", "sha256")):
    lines.append(f"{title}:")
    for rf in index_files:
        size, d = digests(os.path.join(base, rf))
        lines.append(f" {d[algo]} {size:>8} {rf}")
open(os.path.join(base, "Release"), "w").write("\n".join(lines) + "\n")
print(f"indexed {sum(len(v) for v in entries.values())} entries for {', '.join(ARCHES)}")
