#!/usr/bin/env python3
"""Builds the profile artwork: the animated "training run" hero and four project checkpoint cards.

Run after fetch_activity.py:  python3 scripts/generate_dashboard.py   (scripts/build.py runs it for both themes)
The curve in the hero is real data: weekly public contributions from data/activity.json. Stdlib only.
"""
import datetime
import json

import generate_assets as ga
from generate_assets import svg, T, flow, E, BG, PANEL, RULE, TXT, DIM, CY, LM

DATA = json.loads((ga.ROOT / "data" / "activity.json").read_text())
SNAP = DATA["snapshot"]


def weekly():
    """Sum contributions per week (Sunday start) from the daily calendar."""
    days = DATA["days"]
    dts = [datetime.date.fromisoformat(d["date"]) for d in days]
    start = dts[0] - datetime.timedelta(days=(dts[0].weekday() + 1) % 7)
    out = {}
    for d, dt in zip(days, dts):
        k = (dt - start).days // 7
        out[k] = out.get(k, 0) + d["count"]
    return [out[k] for k in sorted(out)]


def smooth(pts):
    """Catmull-Rom to cubic bezier path through pts."""
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d


def reveal(cid, x, y, w, h, body, dur=3.0, delay=0.4):
    """Left-to-right reveal. The un-animated state is the finished drawing."""
    return (f'<clipPath id="{cid}"><rect class="ty" x="{x}" y="{y}" width="{w}" height="{h}" '
            f'style="animation-duration:{dur}s;animation-delay:{delay}s;animation-timing-function:ease-out"/></clipPath>'
            f'<g clip-path="url(#{cid})">{body}</g>')


# ------------------------------------------------------------------- hero
import base64
import math

def b64(name):
    return base64.b64encode((ga.ROOT / "data" / name).read_bytes()).decode()


def hero():
    W, H = 900, 520
    PX, PY, PW, PH = 26, 62, 424, 450          # portrait box (mask is 565x600)
    b = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="{BG}" stroke="{RULE}"/>',
         T(24, 32, "ananyamarghade / README.md", "d", 13), f'<path class="ln" d="M0 46H{W}"/>',
         f'<circle class="l pulse" cx="{W - 150}" cy="28" r="4"/>', T(W - 24, 33, "run in progress", "d", 13, "end")]
    # portrait: the original ASCII art, pre-coloured per theme (scripts/make_portrait.py), plus a moving highlight pass
    base, hl = b64(f"portrait-{ga.THEME}.png"), b64(f"portrait-{ga.THEME}-hl.png")
    img = (f'x="{PX}" y="{PY}" width="{PW}" height="{PH}" preserveAspectRatio="xMidYMid meet"')
    b.append(f'<clipPath id="band"><rect class="scan" x="{PX}" y="{PY}" width="{PW}" height="60"/></clipPath>')
    b.append(f'<image {img} href="data:image/png;base64,{base}"/>')
    b.append(f'<image {img} clip-path="url(#band)" href="data:image/png;base64,{hl}"/>')

    X = 480
    b.append(f'<text class="serif t" x="{X}" y="108" font-size="40">Ananya Marghade<tspan class="l">.</tspan></text>')
    b.append(f'<path class="ln" d="M{X} 124H{W - 28}"/>')
    log = [("role", "B.Tech CSE, AI & Data Science"),
           ("focus", "agents, forecasting, decision support"),
           ("stack", "python java typescript next.js fastapi"),
           ("principle", "evidence before claims"),
           ("status", "open to SDE, AI/ML internships, research")]
    for i, (k, v) in enumerate(log):
        y = 156 + i * 26
        n = len(k) + len(v) + 4
        b.append(f'<clipPath id="c{i}"><rect class="ty" x="{X}" y="{y - 16}" width="{W - X - 20}" height="24" '
                 f'style="animation-delay:{0.4 + i * 1.3}s;animation-duration:1.1s;animation-timing-function:steps({n})"/></clipPath>')
        b.append(f'<g clip-path="url(#c{i})"><text x="{X}" y="{y}" class="l" font-size="13">$</text>'
                 f'<text x="{X + 16}" y="{y}" class="c" font-size="13">{E(k)}</text>'
                 f'<text x="{X + 106}" y="{y}" class="t" font-size="13">{E(v)}</text></g>')
    yc = 156 + 4 * 26
    b.append(f'<rect class="l blink" x="{X + 106 + (len(log[-1][1]) + 1) * 7.8:.0f}" y="{yc - 12}" width="7" height="15"/>')

    # training curve = real weekly public contributions
    wk = weekly()
    x0, x1, yb, yt = X, W - 28, 470, 330
    mx = max(wk) or 1
    pts = [(x0 + (x1 - x0) * i / (len(wk) - 1), yb - (yb - yt - 12) * v / mx) for i, v in enumerate(wk)]
    b.append(T(X, 302, "training curve", "t", 13))
    b.append(T(X + 108, 302, "weekly public contributions, 12 months", "d", 11))
    for gy in (yb, (yb + yt) / 2, yt):
        b.append(f'<path class="ln dash" d="M{x0} {gy:.0f}H{x1}" opacity=".6"/>')
    line = smooth(pts)
    b.append(reveal("rv", 0, 310, W, 170, f'<path d="{line} L{x1} {yb} L{x0} {yb} Z" fill="{CY}" fill-opacity=".10"/>'
                    f'<path class="sc" d="{line}" style="stroke-width:2"/>', 3.2, 0.6))
    px, py = pts[-1]
    b.append(f'<circle class="l pulse" cx="{px:.1f}" cy="{py:.1f}" r="5"/>')
    b.append(T(px - 10, py - 10, "now", "l", 12, "end"))
    top = max(range(len(wk)), key=lambda i: wk[i])
    b.append(f'<circle cx="{pts[top][0]:.1f}" cy="{pts[top][1]:.1f}" r="3.5" fill="{PANEL}" stroke="{CY}" stroke-width="1.5"/>')
    b.append(T(x0, 490, "older", "d", 11))
    b.append(T(x1, 490, f"snapshot {SNAP}", "d", 11, "end"))
    svg("hero.svg", W, H, "Ananya Marghade, profile header",
        "Terminal-style README panel. Left: an ASCII-art portrait of Ananya. Right: the name Ananya Marghade and typed lines. "
        "role: B.Tech CSE, AI and Data Science. focus: agents, forecasting, decision support. stack: python java typescript "
        "next.js fastapi. principle: evidence before claims. status: open to SDE, AI/ML internships and research. Below, an "
        f"animated curve of weekly public GitHub contributions over the last 12 months, snapshot {SNAP}.", "\n".join(b))


# ------------------------------------------------------------ checkpoints
CW, CH = 440, 150
GW, GX, GY, GL = 7.8, 20, 70, 17      # char width, x origin, first baseline, line height


class Grid:
    """Monospace character grid; each placed run is positioned absolutely so art stays aligned in any font."""

    def __init__(self, rows):
        self.rows = [[] for _ in range(rows)]

    def put(self, r, c, text, cls="d"):
        self.rows[r].append((c, text, cls))
        return self

    def svg(self, size=13, group=""):
        out = []
        for r, runs in enumerate(self.rows):
            if not runs:
                continue
            sp = "".join(f'<tspan x="{GX + c * GW:.1f}" class="{cls}">{E(t)}</tspan>' for c, t, cls in sorted(runs))
            out.append(f'<text y="{GY + r * GL}" font-size="{size}">{sp}</text>')
        body = "\n".join(out)
        return f'<g class="{group}">{body}</g>' if group else body


def card(slug, idx, label, title, desc, body):
    b = [f'<rect x=".5" y=".5" width="{CW-1}" height="{CH-1}" rx="8" fill="{PANEL}" stroke="{RULE}"/>',
         T(18, 26, f"checkpoint_{idx:02d}", "l", 12), T(CW - 18, 26, label, "d", 12, "end"),
         f'<path class="ln" d="M0 38H{CW}"/>', body]
    svg(f"cp-{slug}.svg", CW, CH, title, desc, "\n".join(b), bg=False)


def cp_scilens():
    g = Grid(5)
    for r, s in enumerate(["openalex", "semantic", "crossref", "arxiv   "]):
        g.put(r, 0, s, "t")
    g.put(0, 9, "--.", "d").put(1, 9, "--+", "d").put(2, 9, "--+-->", "d").put(3, 9, "--'", "d")
    g.put(2, 16, "[extract]", "t seq").put(2, 26, "-->", "d").put(2, 30, "[critic]", "c seq s1")
    g.put(2, 39, "-->", "d").put(2, 43, "gap", "l seq s2")
    g.put(3, 20, "^", "d").put(3, 34, "|", "d")
    g.put(4, 20, "'", "d").put(4, 21, "- re-search -", "l seq s3").put(4, 34, "'", "d")
    return g.svg()


def cp_opd():
    g = Grid(5)
    cols = 32
    for i in range(cols):
        v = 0.12 + 0.62 * i / (cols - 1) + 0.06 * math.sin(i * 0.9)
        r = min(max(4 - round(v * 4.6), 0), 4)
        g.put(r, i, "*", "c")
    for i in range(0, 46):
        g.put(1, i, "-" if i % 2 == 0 else " ", "d")
    g.put(0, 0, "overload threshold", "d")
    for k, i in enumerate(range(33, 41, 2)):
        g.put(2 - (k // 2), i, ".", "l seq s" + str(k % 4))
    g.put(0, 42, "?", "l seq s3").put(0, 44, "+3d", "l")
    g.put(4, 0, "daily load", "d")
    return g.svg()


def cp_lru():
    g_a, g_b = Grid(5), Grid(5)
    for g, order, tag in ((g_a, ["k=3", "k=1", "k=7"], "before"), (g_b, ["k=7", "k=3", "k=1"], "after")):
        g.put(0, 0, "$ get(7)", "l" if tag == "after" else "d")
        g.put(2, 0, "HEAD", "d")
        for j, k in enumerate(order):
            col = 9 + j * 10
            g.put(2, col - 4, "<->", "d").put(2, col, f"[{k}]", "l" if k == "k=7" else "t")
        g.put(2, 35, "<->", "d").put(2, 39, "TAIL", "d")
    g_a.put(3, 29, "^ next out", "d").put(4, 0, "before: k=7 sits next to the tail", "d")
    g_b.put(3, 9, "^ front", "l").put(3, 29, "^ next out", "d").put(4, 0, "after: k=7 moved to the front", "l")
    return g_a.svg(group="altA") + "\n" + g_b.svg(group="altB")


def cp_drowsy():
    g = Grid(5)
    cols = 38
    lvl = [0] * cols
    for c in (5, 6, 14, 15):
        lvl[c] = 2
    for c in range(24, 33):
        lvl[c] = 4
    for i, l in enumerate(lvl):
        g.put(l, i, "*", "c")
        if i and lvl[i] != lvl[i - 1]:
            for rr in range(min(lvl[i], lvl[i - 1]) + 1, max(lvl[i], lvl[i - 1])):
                g.put(rr, i if lvl[i] > lvl[i - 1] else i - 1, "|", "d")
    for i in range(0, cols + 4):
        if lvl[i] != 3 if i < cols else True:
            g.put(3, i, "." if i % 2 == 0 else " ", "d")
    g.put(1, 26, "closed", "d").put(3, 44, "limit", "d")
    g.put(4, 34, "<- ALERT", "l blink")
    g.put(0, 40, "EAR", "d")
    return g.svg()


def checkpoints():
    card("scilens", 1, "research agent", "SciLens pipeline",
         "ASCII diagram. Four sources (openalex, semantic scholar, crossref, arxiv) feed extract, then critic, then gap, with a re-search loop from critic back to extract.", cp_scilens())
    card("opd", 2, "forecasting", "Hospital OPD forecasting",
         "ASCII plot, illustrative. Daily load rises toward an overload threshold; dots project three days ahead to a question mark.", cp_opd())
    card("lru", 3, "systems", "LRU cache",
         "ASCII diagram alternating between before and after get(7): key 7 moves from next to the tail to the front of the list.", cp_lru())
    card("drowsiness", 4, "computer vision", "Drowsiness detection",
         "ASCII plot, illustrative. Eye aspect ratio blinks stay above a limit; one long closure drops below it and raises an alert.", cp_drowsy())


if __name__ == "__main__":
    hero(); checkpoints()
