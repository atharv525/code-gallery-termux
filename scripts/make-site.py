#!/usr/bin/env python3
"""Generate the Code Gallery docs site (out/index.html) from package metadata.

Reads every packages/<name>/build.conf and renders one card per package with
its description, what it does, how to install it and how to use it. Runs in CI
on every push, so adding a new package automatically adds it to the site.
"""
import os, subprocess, html, json, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKGDIR = os.path.join(ROOT, "packages")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "out")
PAGES_BASE = "https://atharv525.github.io/code-gallery-termux"

FIELDS = ["NAME", "VERSION", "ARCH", "SECTION", "DEPENDS", "RECOMMENDS",
          "SUGGESTS", "DESCRIPTION", "LONG_DESCRIPTION", "USAGE", "TOOLS"]


def read_conf(path):
    """Source a build.conf in bash and read every field back safely."""
    sep = "\x1e"
    script = ". '%s'\n" % path + "".join(
        'printf "%%s%s" "${%s:-}"\n' % (sep, f) for f in FIELDS)
    out = subprocess.run(["bash", "-c", script], capture_output=True,
                         text=True).stdout
    parts = out.split(sep)
    return {f: parts[i].strip() for i, f in enumerate(FIELDS) if i < len(parts)}


def packages():
    res = []
    for name in sorted(os.listdir(PKGDIR)):
        if name == "_template":
            continue
        conf = os.path.join(PKGDIR, name, "build.conf")
        if os.path.isfile(conf):
            d = read_conf(conf)
            d.setdefault("NAME", name)
            res.append(d)
    # put cg-bugbounty and cg-devkit first, rest alphabetical
    order = {"cg-bugbounty": 0, "cg-devkit": 1, "cg-setup": 2}
    res.sort(key=lambda p: (order.get(p["NAME"], 9), p["NAME"]))
    return res


def e(s):
    return html.escape(s or "")


def tools_html(raw):
    out = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        grp, rest = line.split(":", 1)
        chips = "".join('<span class="chip">%s</span>' % e(t)
                        for t in rest.split())
        out.append('<div class="grp"><b>%s</b>%s</div>' % (e(grp), chips))
    return '<div class="tools">%s</div>' % "".join(out) if out else ""


def card(p):
    name = p["NAME"]
    long_desc = e(p.get("LONG_DESCRIPTION") or p.get("DESCRIPTION", "")
                  ).replace("\n", "<br>")
    install = "pkg install %s" % name
    usage = p.get("USAGE") or install
    deps = p.get("DEPENDS", "")
    tools = tools_html(p.get("TOOLS", ""))
    deps_html = ('<p class="deps"><b>Depends:</b> %s</p>' % e(deps)) if deps else ""
    return """
    <article class="card" id="{id}">
      <div class="chead">
        <h3>{name}</h3>
        <span class="ver">v{ver}</span>
      </div>
      <p class="desc">{desc}</p>
      {tools}
      <div class="block"><span class="lbl">Install</span>
        <pre><code>{install}</code></pre></div>
      <div class="block"><span class="lbl">Use</span>
        <pre><code>{usage}</code></pre></div>
      {deps}
    </article>""".format(
        id=e(name), name=e(name), ver=e(p.get("VERSION", "")),
        desc=long_desc, tools=tools, install=e(install),
        usage=e(usage), deps=deps_html)


def build():
    pkgs = packages()
    cards = "\n".join(card(p) for p in pkgs)
    nav = "".join('<a href="#%s">%s</a>' % (e(p["NAME"]), e(p["NAME"]))
                  for p in pkgs)
    today = datetime.date.today().isoformat()
    page = PAGE.format(cards=cards, nav=nav, count=len(pkgs),
                       base=PAGES_BASE, updated=today)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "index.html"), "w") as f:
        f.write(page)
    print("wrote %s/index.html with %d packages" % (OUT, len(pkgs)))


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Code Gallery — Termux APT repo</title>
<style>
  :root {{
    --bg:#0d1117; --card:#161b22; --line:#30363d; --fg:#e6edf3;
    --muted:#8b949e; --accent:#2f81f7; --green:#3fb950; --code:#0b0f14;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg);
    font:16px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif; }}
  a {{ color:var(--accent); text-decoration:none; }}
  .wrap {{ max-width:960px; margin:0 auto; padding:0 20px 64px; }}
  header.hero {{ text-align:center; padding:56px 20px 28px; }}
  .hero h1 {{ font-size:2.4rem; margin:0 0 6px;
    background:linear-gradient(90deg,#2f81f7,#3fb950);
    -webkit-background-clip:text; background-clip:text; color:transparent; }}
  .hero p {{ color:var(--muted); margin:0 auto; max-width:620px; }}
  .install-one {{ background:var(--code); border:1px solid var(--line);
    border-radius:12px; padding:16px; margin:22px auto 0; max-width:720px;
    overflow:auto; }}
  .install-one code {{ color:var(--green); white-space:pre; }}
  .pills {{ display:flex; gap:10px; justify-content:center; flex-wrap:wrap;
    margin-top:16px; }}
  .pills a {{ border:1px solid var(--line); border-radius:999px;
    padding:6px 14px; color:var(--fg); font-size:.9rem; }}
  .nav {{ display:flex; gap:8px; flex-wrap:wrap; margin:26px 0 10px; }}
  .nav a {{ border:1px solid var(--line); border-radius:8px; padding:4px 10px;
    font-size:.82rem; color:var(--muted); }}
  .nav a:hover {{ color:var(--fg); border-color:var(--accent); }}
  .grid {{ display:grid; gap:16px; }}
  .card {{ background:var(--card); border:1px solid var(--line);
    border-radius:14px; padding:18px 20px; scroll-margin-top:20px; }}
  .chead {{ display:flex; align-items:center; gap:10px; }}
  .chead h3 {{ margin:0; font-family:ui-monospace,Menlo,monospace;
    font-size:1.15rem; color:#79c0ff; }}
  .ver {{ font-size:.75rem; color:var(--muted); border:1px solid var(--line);
    border-radius:999px; padding:1px 8px; }}
  .desc {{ color:var(--fg); margin:10px 0 12px; }}
  .block {{ margin:10px 0; }}
  .lbl {{ display:inline-block; font-size:.72rem; letter-spacing:.06em;
    text-transform:uppercase; color:var(--muted); margin-bottom:4px; }}
  pre {{ margin:0; background:var(--code); border:1px solid var(--line);
    border-radius:10px; padding:12px 14px; overflow:auto; }}
  code {{ font-family:ui-monospace,Menlo,monospace; font-size:.88rem; }}
  pre code {{ color:#e6edf3; white-space:pre; }}
  .deps {{ color:var(--muted); font-size:.82rem; margin:10px 0 0; }}
  .tools {{ display:grid; gap:6px; margin:4px 0 12px; }}
  .grp b {{ display:inline-block; min-width:92px; color:var(--green);
    font-size:.82rem; text-transform:uppercase; letter-spacing:.04em; }}
  .chip {{ display:inline-block; background:#0b0f14; border:1px solid var(--line);
    border-radius:6px; padding:2px 8px; margin:3px 4px 0 0; font-size:.8rem;
    font-family:ui-monospace,Menlo,monospace; color:#adbac7; }}
  footer {{ text-align:center; color:var(--muted); font-size:.82rem;
    margin-top:44px; }}
</style>
</head>
<body>
<header class="hero">
  <h1>Code Gallery</h1>
  <p>A signed APT repository for Termux. Extra coding and bug-bounty tools that
     aren't in the official repos — install them like any package.</p>
  <div class="install-one"><code>curl -sL {base}/install.sh | bash</code></div>
  <div class="pills">
    <a href="https://github.com/atharv525/code-gallery-termux">GitHub</a>
    <a href="{base}/install.sh">install.sh</a>
    <a href="{base}/uninstall.sh">uninstall.sh</a>
    <a href="{base}/packages.json">packages.json</a>
  </div>
</header>
<div class="wrap">
  <p style="color:var(--muted)">After the one-time install, update and grab any
     tool:</p>
  <pre><code>pkg update
pkg install cg-bugbounty</code></pre>
  <nav class="nav">{nav}</nav>
  <div class="grid">
{cards}
  </div>
  <footer>
    {count} packages · auto-generated from package metadata · updated {updated}<br>
    Use security tools only on targets you are authorised to test.
  </footer>
</div>
</body>
</html>"""


if __name__ == "__main__":
    build()
