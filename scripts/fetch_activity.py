#!/usr/bin/env python3
"""Snapshots PUBLIC GitHub activity into data/activity.json (stdlib only).

Parses the public contribution-calendar HTML, so it can break if GitHub changes
its markup. Re-run, then re-run generate_dashboard.py, to refresh the dashboard.
"""
import datetime
import html
import json
import pathlib
import re
import sys
import urllib.request

USER = "ananyamarghade"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "activity.json"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")


def scrape_repos():
    repos, seen = [], set()
    for page in range(1, 11):
        new = 0
        for blk in re.findall(r'<li[^>]*itemprop="owns"[^>]*>(.*?)</li>',
                              get(f"https://github.com/{USER}?tab=repositories&page={page}"), re.S):
            n = re.search(r'codeRepository"[^>]*>\s*([^<\s]+)', blk)
            if not n or n.group(1) in seen:
                continue
            l = re.search(r'itemprop="programmingLanguage">([^<]+)', blk)
            seen.add(n.group(1)); new += 1
            repos.append({"name": n.group(1), "lang": html.unescape(l.group(1)) if l else None})
        if not new:
            break
    return repos


repos = scrape_repos()
if not repos:
    sys.exit("Could not parse the repository list; GitHub markup may have changed.")
cal = get(f"https://github.com/users/{USER}/contributions")
prof = get(f"https://github.com/{USER}")

cells = {}
for tag in re.findall(r"<td\b[^>]*>", cal):
    d, i, l = (re.search(rf'{k}="([^"]*)"', tag) for k in ("data-date", "id", "data-level"))
    if d and i and l:
        cells[i.group(1)] = {"date": d.group(1), "level": int(l.group(1)), "count": 0}
for cid, text in re.findall(r'<tool-tip[^>]*\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>', cal):
    m = re.match(r"\s*(No|\d+)\s+contribution", text)
    if m and cid in cells:
        cells[cid]["count"] = 0 if m.group(1) == "No" else int(m.group(1))
days = sorted(cells.values(), key=lambda c: c["date"])
if not days:
    sys.exit("Could not parse the contribution calendar; GitHub markup may have changed.")

tot = re.search(r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year", cal)
fol = re.search(r'text-bold color-fg-default">([\d.,kK]+)</span>\s*followers', prof)
data = {
    "snapshot": datetime.date.today().isoformat(),
    "total": int(tot.group(1).replace(",", "")) if tot else sum(d["count"] for d in days),
    "followers": fol.group(1) if fol else None,
    "public_repos": len(repos),
    "repos": repos,
    "days": days,
}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(data), encoding="utf-8")
print(f"{len(days)} days, total={data['total']}, followers={data['followers']}, "
      f"active days={sum(d['count'] > 0 for d in days)}")
