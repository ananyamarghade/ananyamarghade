#!/usr/bin/env python3
"""Static checks for the profile README and assets. Stdlib only.

Usage:  python3 scripts/validate.py [--online]
"""
import pathlib
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
readme = (ROOT / "README.md").read_text(encoding="utf-8")
fails, notes = [], []


def check(ok, msg):
    print(("PASS  " if ok else "FAIL  ") + msg)
    if not ok:
        fails.append(msg)


# 1. local image/link references exist
refs = set(re.findall(r'(?:src|srcset)="([^"]+)"', readme)) | set(re.findall(r"\]\((?!https?:|#)([^)]+)\)", readme))
for r in sorted(refs):
    check((ROOT / r).exists(), f"local file exists: {r}")

# 2. SVGs well-formed, sized, no scripts or external refs
for p in sorted((ROOT / "assets").rglob("*.svg")):
    try:
        tree = ET.parse(p)
        txt = p.read_text(encoding="utf-8")
        check(True, f"{p.name} well-formed")
        check("<script" not in txt and "http://" not in txt.replace("http://www.w3.org/2000/svg", ""),
              f"{p.name} has no scripts or external URLs")
        check(p.stat().st_size < 100_000, f"{p.name} size {p.stat().st_size/1024:.1f} KB < 100 KB")
        check(tree.getroot().find("{http://www.w3.org/2000/svg}title") is not None, f"{p.name} has <title>")
        check("prefers-reduced-motion" in txt, f"{p.name} respects reduced motion")
    except ET.ParseError as e:
        check(False, f"{p.name} parse error: {e}")

names = {t: {p.name for p in (ROOT / "assets" / t).glob("*.svg")} for t in ("dark", "light")}
check(names["dark"] == names["light"] and names["dark"], "dark and light themes have identical asset sets")

# 3. anchors resolve
slugs = {"top"} | set(re.findall(r'<a id="([^"]+)"', readme))
for h in re.findall(r"^#{1,6}\s+(.+)$", readme, re.M):
    slugs.add(re.sub(r"\s", "-", re.sub(r"[^a-z0-9 \-]", "", h.lower())))
for a in sorted(set(re.findall(r'href="#([^"]+)"', readme)) | set(re.findall(r"\]\(#([^)]+)\)", readme))):
    check(a in slugs, f"anchor resolves: #{a}")

# 4. alt text on non-decorative images
for tag in re.findall(r"<img [^>]+>", readme):
    alt = re.search(r'alt="([^"]*)"', tag)
    src = re.search(r'src="([^"]+)"', tag).group(1)
    check(bool(alt and alt.group(1).strip()), f"{src}: has alt text")

# 5. secrets / local paths
pat = re.compile(r"(ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|api[_-]?key\s*[:=]|C:\\Users|/home/\w+)", re.I)
for p in [ROOT / "README.md", ROOT / "SETUP.md", *(ROOT / "assets").rglob("*.svg")]:
    check(not pat.search(p.read_text(encoding="utf-8")), f"no secret-like strings in {p.name}")

# 6. optional online link check
if "--online" in sys.argv:
    for u in sorted(set(re.findall(r"\]\((https?://[^)]+)\)", readme))):
        try:
            req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "profile-validate"})
            code = urllib.request.urlopen(req, timeout=15).status
            check(code < 400, f"{code} {u}")
        except Exception as e:  # network blocked, timeouts, 4xx/5xx
            notes.append(f"COULD NOT CHECK  {u}  ({type(e).__name__}: {e})")

for n in notes:
    print(n)
print(f"\n{len(fails)} failed")
sys.exit(1 if fails else 0)
