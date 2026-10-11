#!/usr/bin/env python3
"""Generates identity, dashboard, system-map and section-header SVGs.

Run after fetch_activity.py:  python3 scripts/generate_dashboard.py
Reuses helpers from generate_assets.py. Stdlib only.
"""
import collections
import datetime
import json

import generate_assets as ga
from generate_assets import svg, T, flow, E, BG, PANEL, RULE, TXT, DIM, CY, LM

ga.CSS += """
.cell{animation:cin .5s ease-out both}
@keyframes cin{from{opacity:0}to{opacity:1}}
"""
DATA = json.loads((ga.ROOT / "data" / "activity.json").read_text())
SNAP = DATA["snapshot"]
FOLLOWERS = DATA["followers"] or "-"


def lang_rows():
    names = {"PLSQL": "PL/SQL"}
    c = collections.Counter(names.get(r["lang"], r["lang"]) if r["lang"] else "no language" for r in DATA["repos"])
    rows = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))
    if len(rows) > 10:
        rows = rows[:9] + [(f"other ({len(rows) - 9})", sum(n for _, n in rows[9:]))]
    return rows


LANGS = lang_rows()


# ---------------------------------------------------------------- sections
def section(slug, label, meta=""):
    lw = 30 + len(label) * 10.8 + 14
    mw = len(meta) * 7.4 + 16 if meta else 0
    b = [T(0, 27, "##", "l", 16), T(30, 27, label, "t", 18)]
    d = f"M{lw:.0f} 22H{900 - mw:.0f}"
    b += [f'<path class="ln" d="{d}"/>', flow(d, False, 0, "4 96")]
    if meta:
        b.append(T(900, 27, meta, "d", 13, "end"))
    svg(f"section-{slug}.svg", 900, 40, f"Section: {label}",
        f"Section header: {label}{', ' + meta if meta else ''}.", "\n".join(b))


# ------------------------------------------------------------- ascii art
def ascii_net(cols=44, rows=22):
    g = [[" "] * cols for _ in range(rows)]
    layers = [(4, [4, 11, 18]), (15, [2, 8, 14, 20]), (27, [4, 11, 18]), (39, [11])]

    def line(x0, y0, x1, y1):
        n = max(abs(x1 - x0), abs(y1 - y0))
        for s in range(n + 1):
            x = round(x0 + (x1 - x0) * s / n)
            y = round(y0 + (y1 - y0) * s / n)
            if g[y][x] == " ":
                g[y][x] = ":"
    for (xa, ya), (xb, yb) in zip(layers, layers[1:]):
        for y1 in ya:
            for y2 in yb:
                line(xa, y1, xb, y2)
    hot = {(4, 4), (15, 8), (27, 18), (39, 11)}
    for x, ys in layers:
        for y in ys:
            g[y][x] = "@" if (x, y) in hot else "O"
    return ["".join(r) for r in g]


def ascii_text(lines, x0, y0, lh, cw, size):
    out = []
    cls = {":": "d", "O": "c", "@": "l"}
    for ri, row in enumerate(lines):
        runs, i = [], 0
        while i < len(row):
            if row[i] == " ":
                i += 1
                continue
            j = i
            while j < len(row) and row[j] == row[i]:
                j += 1
            runs.append((i, row[i], j - i))
            i = j
        spans = "".join(f'<tspan x="{x0 + c * cw:.1f}" class="{cls[ch]}">{ch * n}</tspan>' for c, ch, n in runs)
        out.append(f'<text y="{y0 + ri * lh}" font-size="{size}">{spans}</text>')
    return "\n".join(out)


# ---------------------------------------------------------------- identity
def identity():
    """Neofetch-style panel: ASCII network on the left, dotted-leader key/value rows on the right."""
    W, H = 900, 480
    CW, X0, X1, SZ = 7.2, 404, 868, 12
    b = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="{BG}" stroke="{RULE}"/>',
         T(24, 32, "ananyamarghade / README.md", "d", 13), f'<path class="ln" d="M0 46H{W}"/>']
    b.append(ascii_text(ascii_net(), 32, 92, 16, 7.8, 13))
    ec = ga.ecg(32, 372, 452, 113)
    b += [f'<path class="ln" d="{ec}"/>', flow(ec, False, 0, "14 86")]
    rows = [("name", "ananya@marghade"),
            ("kv", "Role", "B.Tech CSE, AI & Data Science"),
            ("kv", "Focus", "AI engineering, software, data systems"),
            ("kv", "Building", "agents, forecasting, decision support"),
            ("kv", "Seeking", "SDE and AI/ML internships, research"),
            ("kv", "Team", "DimensionAI, lead on Aasha"),
            ("gap",),
            ("kv", "Languages.Main", "Python, Java, TypeScript, JavaScript, C"),
            ("kv", "Languages.Other", "SQL (PL/SQL), Assembly, Lex"),
            ("kv", "ML", "LangGraph, Random Forest, OpenCV, Dlib"),
            ("kv", "Web", "FastAPI, Gradio, Next.js, Tailwind, Supabase"),
            ("gap",),
            ("sect", f"GitHub Stats, {SNAP}"),
            ("kv", "Repos", f"{DATA['public_repos']} public"),
            ("kv", "Contributions", f"{DATA['total']} in the last 12 months"),
            ("kv", "Followers", str(FOLLOWERS)),
            ("gap",),
            ("sect", "Contact"),
            ("kv", "GitHub", "github.com/ananyamarghade")]
    y, n = 84, 0
    for r in rows:
        dl = f"animation-delay:{n * 0.07:.2f}s"
        if r[0] == "gap":
            y += 12
            continue
        if r[0] in ("name", "sect"):
            label = r[1]
            cls = "c" if r[0] == "name" else "l"
            sz = 15 if r[0] == "name" else SZ
            b.append(T(X0, y, label, cls + " cell", sz, extra=f'style="{dl}"'))
            x0 = X0 + len(label) * (sz * 0.6) + 10
            b.append(f'<path class="ln" d="M{x0:.0f} {y - 4}H{X1}"/>')
            y += 22
        else:
            key, val = r[1] + ":", r[2]
            xa, xb = X0 + (len(key) + 1) * CW, X1 - (len(val) + 1) * CW
            b.append(T(X0, y, key, "c cell", SZ, extra=f'style="{dl}"'))
            b.append(f'<path d="M{xa:.0f} {y - 3}H{xb:.0f}" stroke="{DIM}" stroke-opacity=".6" stroke-width="1.4" '
                     f'stroke-linecap="round" stroke-dasharray="0.1 5" fill="none"/>')
            b.append(T(X1, y, val, "t cell", SZ, "end", extra=f'style="{dl}"'))
            y += 19
        n += 1
    svg("identity.svg", W, H, "Ananya Marghade, developer profile",
        "Terminal-style profile panel. Left: ASCII art of a layered neural network. Right: ananya@marghade. "
        "B.Tech CSE, AI and Data Science. Focus on AI engineering, software, data systems and research. Building "
        "agents, forecasting and decision support. Seeking SDE and AI/ML internships and research. DimensionAI, lead "
        "on Aasha. Languages: Python, Java, TypeScript, JavaScript, C, SQL, Assembly, Lex. ML: LangGraph, Random "
        "Forest, OpenCV, Dlib. Web: FastAPI, Gradio, Next.js, Tailwind, Supabase. "
        f"GitHub snapshot {SNAP}: {DATA['public_repos']} public repos, {DATA['total']} contributions in the last "
        f"12 months, {FOLLOWERS} followers. Contact: github.com/ananyamarghade.", "\n".join(b))


# --------------------------------------------------------------- dashboard
def dashboard():
    """Contribution heatmap only; the numbers live in the identity panel."""
    W, H = 900, 180
    days = DATA["days"]
    dts = [datetime.date.fromisoformat(d["date"]) for d in days]
    start = dts[0] - datetime.timedelta(days=(dts[0].weekday() + 1) % 7)
    lvl = ga.LEVELS
    active = sum(d["count"] > 0 for d in days)
    X0 = 150
    b = []
    seen = set()
    for d, dt in zip(days, dts):
        off = (dt - start).days
        col, row = off // 7, off % 7
        if (dt.day <= 7 and dt.month not in seen and row == 0) or (dt.day == 1 and dt.month not in seen):
            seen.add(dt.month)
            b.append(T(X0 + col * 11, 36, dt.strftime("%b"), "d", 11))
        b.append(f'<rect class="cell" x="{X0 + col * 11}" y="{44 + row * 11}" width="9" height="9" '
                 f'fill="{lvl[d["level"]]}" style="animation-delay:{col * 0.03:.2f}s"/>')
    b.append(T(X0, 146, "less", "d", 12))
    for i, c in enumerate(lvl):
        b.append(f'<rect x="{X0 + 38 + i * 13}" y="137" width="9" height="9" fill="{c}"/>')
    b.append(T(X0 + 108, 146, "more", "d", 12))
    b.append(T(X0, 172, f"public contributions only, snapshot {SNAP}. Activity, not skill.",
               "d", 12))
    svg("dashboard.svg", W, H, "GitHub activity",
        f"Snapshot {SNAP}. {DATA['total']} public contributions in the last 12 months across {active} active days, "
        "Contribution heatmap.", "\n".join(b))


# -------------------------------------------------------------- system map
def toolkit_map():
    W, H = 900, 440
    cx = [40, 250, 460, 670]
    ry = lambda r: 84 + r * 46
    nodes = {"Python": (0, 0), "JavaScript": (0, 1), "C": (0, 2), "TypeScript": (0, 3), "SQL": (0, 4), "Java": (0, 5),
             "LangGraph": (1, 0), "Random Forest": (1, 1), "OpenCV + Dlib": (1, 2), "Maven": (1, 5),
             "FastAPI": (2, 0), "Gradio": (2, 1), "Next.js": (2, 3), "Tailwind + Radix": (2, 4),
             "Vercel": (3, 0), "Supabase": (3, 3), "Netlify": (3, 4)}
    unlinked = {"JavaScript", "C", "SQL", "Tailwind + Radix"}
    b = []
    for x, lab in zip(cx, ["languages", "ml and build", "backend and ui", "data and ship"]):
        b.append(T(x, 58, lab, "d", 13))
        b.append(f'<path class="ln" d="M{x} 68H{x + 150}"/>')

    def out(n):
        c, r = nodes[n]
        return cx[c] + 150, ry(r) + 16

    def inn(n):
        c, r = nodes[n]
        return cx[c], ry(r) + 16

    def route(a, z, color, dash=False, w=2):
        (x0, y0), (x1, y1) = out(a), inn(z)
        d = f"M{x0} {y0}C{x0 + 40} {y0} {x1 - 40} {y1} {x1} {y1}"
        da = ' stroke-dasharray="5 4"' if dash else ""
        b.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity=".5" stroke-width="{w}"{da}/>')
        b.append(f'<path class="flow" pathLength="100" d="{d}" style="stroke:{color};stroke-width:{w + .6}"/>')

    route("Python", "LangGraph", CY); route("LangGraph", "FastAPI", CY); route("FastAPI", "Vercel", CY)
    route("LangGraph", "Gradio", CY, w=1.4); route("Gradio", "Vercel", CY, w=1.4)
    route("Python", "Random Forest", LM); route("Python", "OpenCV + Dlib", LM)
    route("TypeScript", "Next.js", TXT); route("Next.js", "Supabase", TXT); route("Next.js", "Netlify", TXT)
    route("Java", "Maven", CY, dash=True)
    # short vertical link Next.js -> Tailwind + Radix
    nx = cx[2] + 75
    b.append(f'<path class="ar" d="M{nx} {ry(3) + 32}V{ry(4)}"/>')
    for n, (c, r) in nodes.items():
        dim = n in unlinked
        b.append(f'<rect class="box" x="{cx[c]}" y="{ry(r)}" width="150" height="32"/>')
        b.append(T(cx[c] + 75, ry(r) + 20.5, n, "d" if dim else "t", 13, "middle"))
    b.append(T(40, 372, "also: Git; Assembly (microcontrollers lab); Lex (compiler lab); C, SQL, JavaScript (coursework labs)",
               "d", 12))
    leg = [("SciLens", CY, False), ("OPD, drowsiness", LM, False), ("SenentialAI", TXT, False), ("LRU cache", CY, True)]
    for i, (name, col, dash) in enumerate(leg):
        x = 40 + i * 200
        da = ' stroke-dasharray="5 4"' if dash else ""
        b.append(f'<path d="M{x} 408H{x + 28}" stroke="{col}" stroke-width="2.2" fill="none"{da}/>')
        b.append(T(x + 38, 412, name, "t", 13))
    svg("toolkit-map.svg", W, H, "Technology system map",
        "Four columns (languages, ML and build, backend and UI, data and ship) with project routes drawn through them. "
        "SciLens: Python, LangGraph, FastAPI and Gradio, Vercel. OPD forecasting and drowsiness detection: Python to "
        "Random Forest and OpenCV with Dlib. SenentialAI: TypeScript, Next.js, Supabase and Netlify. LRU cache: Java "
        "and Maven. C, SQL and JavaScript are from coursework labs.", "\n".join(b))


if __name__ == "__main__":
    identity(); dashboard()
