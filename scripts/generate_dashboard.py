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
def hero():
    W, H = 900, 470
    b = [f'<pattern id="g" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" class="ln"/></pattern>',
         f'<rect width="{W}" height="{H}" fill="url(#g)" opacity=".3"/>',
         f'<path class="ln" d="M48 58H852"/>',
         T(48, 40, "~/ananyamarghade  $ python run.py", "d", 14),
         f'<circle class="l pulse" cx="740" cy="35" r="4"/>',
         T(852, 40, "run in progress", "d", 14, "end")]
    b.append('<text class="serif t" x="44" y="132" font-size="64">Ananya Marghade<tspan class="l">.</tspan></text>')
    log = [("ananya --role", "B.Tech CSE, AI & Data Science"),
           ("ananya --focus", "agents, forecasting, decision support"),
           ("ananya --stack", "python java typescript next.js fastapi"),
           ("ananya --principle", "evidence before claims"),
           ("ananya --status", "open to SDE, AI/ML internships, research")]
    for i, (cmd, out) in enumerate(log):
        y = 170 + i * 24
        n = len(cmd) + len(out) + 6
        b.append(f'<clipPath id="c{i}"><rect class="ty" x="48" y="{y - 17}" width="620" height="24" '
                 f'style="animation-delay:{0.4 + i * 1.5}s;animation-duration:1.3s;animation-timing-function:steps({n})"/></clipPath>')
        b.append(f'<g clip-path="url(#c{i})"><text x="48" y="{y}" class="l" font-size="15">$</text>'
                 f'<text x="66" y="{y}" class="d" font-size="15">{E(cmd)}</text>'
                 f'<text x="252" y="{y}" class="t" font-size="15">{E(out)}</text></g>')
    ycur = 170 + 4 * 24
    b.append(f'<rect class="l blink" x="{252 + (len(log[-1][1]) + 1) * 9:.0f}" y="{ycur - 13}" width="8" height="16"/>')

    # training curve = real weekly public contributions
    wk = weekly()
    x0, x1, yb, yt = 48, 852, 440, 300
    mx = max(wk) or 1
    pts = [(x0 + (x1 - x0) * i / (len(wk) - 1), yb - (yb - yt - 14) * v / mx) for i, v in enumerate(wk)]
    for gy in (yb, (yb + yt) / 2, yt):
        b.append(f'<path class="ln dash" d="M{x0} {gy:.0f}H{x1}" opacity=".6"/>')
    line = smooth(pts)
    area = line + f" L{x1} {yb} L{x0} {yb} Z"
    b.append(reveal("rv", 0, 280, 900, 180, f'<path d="{area}" fill="{CY}" fill-opacity=".10"/>'
                    f'<path class="sc" d="{line}" style="stroke-width:2.2"/>', 3.2, 0.6))
    px, py = pts[-1]
    b.append(f'<circle class="l pulse" cx="{px:.1f}" cy="{py:.1f}" r="6"/>')
    b.append(T(px - 12, py - 12, "now", "l", 13, "end"))
    top = max(range(len(wk)), key=lambda i: wk[i])
    b.append(f'<circle cx="{pts[top][0]:.1f}" cy="{pts[top][1]:.1f}" r="4" fill="{PANEL}" stroke="{CY}" stroke-width="1.6"/>')
    b.append(T(x0, 290, "training curve", "t", 14))
    b.append(T(x0 + 118, 290, "weekly public contributions, last 12 months. Real data, refreshed daily.", "d", 13))
    b.append(T(x1, 462, f"snapshot {SNAP}", "d", 12, "end"))
    b.append(T(x0, 462, "older", "d", 12))
    svg("hero.svg", W, H, "Ananya Marghade, profile header",
        "Terminal-style header. Name: Ananya Marghade. Typed lines: B.Tech CSE, AI and Data Science; agents, forecasting "
        "and decision support; python, java, typescript, next.js, fastapi; evidence before claims; open to SDE and AI/ML "
        "internships and research. Below it, an animated curve of my weekly public GitHub contributions over the last "
        f"12 months, snapshot {SNAP}.", "\n".join(b))


# ------------------------------------------------------------ checkpoints
CW, CH = 440, 150


def card(slug, idx, label, title, desc, body):
    b = [f'<rect x=".5" y=".5" width="{CW-1}" height="{CH-1}" rx="8" fill="{PANEL}" stroke="{RULE}"/>',
         T(18, 26, f"checkpoint_{idx:02d}", "l", 12), T(CW - 18, 26, label, "d", 12, "end"),
         f'<path class="ln" d="M0 38H{CW}"/>'] + body
    svg(f"cp-{slug}.svg", CW, CH, title, desc, "\n".join(b), bg=False)


def cp_scilens():
    srcs = ["OpenAlex", "Semantic Scholar", "CrossRef", "arXiv"]
    b = []
    for i, s in enumerate(srcs):
        y = 58 + i * 20
        b.append(T(18, y + 4, s, "d", 11))
        b.append(f'<path class="ln" d="M130 {y}L196 98"/>')
        b.append(flow(f"M130 {y}L196 98", i % 2 == 1, i * 0.7))
    b.append(f'<rect class="box" x="196" y="82" width="74" height="32"/>' + T(233, 102, "extract", "t", 12, "middle"))
    b.append(f'<path class="ln" d="M270 98H316"/>' + flow("M270 98H316", False, 0.4))
    b.append(f'<rect class="box" x="316" y="82" width="62" height="32"/>' + T(347, 102, "critic", "c", 12, "middle"))
    b.append(f'<path class="ar dash" d="M347 82V66H233V82" marker-end="url(#ar)"/>')
    b.append(f'<circle class="l pulse" cx="405" cy="98" r="7"/>' + f'<path class="ln" d="M378 98H398"/>')
    b.append(T(405, 124, "gap", "l", 11, "middle"))
    b.append(T(290, 62, "re-search", "d", 10, "middle"))
    b.append(T(18, 142, "papers  >  methods  >  evidence-checked gaps", "d", 11))
    return b


def cp_opd():
    b = []
    base = 120
    ys = [100, 92, 96, 84, 90, 74, 80, 66, 72, 60, 68, 58]
    pts = [(24 + i * 22, y) for i, y in enumerate(ys)]
    b.append(f'<rect x="{pts[-1][0]}" y="48" width="{CW - 24 - pts[-1][0] - 30 + 24}" height="{base - 48}" fill="{CY}" fill-opacity=".08"/>')
    b.append(f'<path class="ln dash" d="M18 70H{CW - 18}"/>' + T(24, 64, "overload threshold", "d", 11))
    d = smooth(pts)
    b.append(reveal("rv", 0, 40, CW, 90, f'<path class="sc" d="{d}"/>', 2.4, 0.3))
    b.append(f'<path class="ln dash" d="M{pts[-1][0]} {pts[-1][1]}L{CW - 56} 52" stroke="{LM}"/>')
    b.append(f'<circle class="l pulse" cx="{CW - 56}" cy="52" r="6"/>' + T(CW - 68, 56, "+3 days?", "l", 11, "end"))
    b.append(f'<path class="ln" d="M18 {base}H{CW - 18}"/>' + T(24, 142, "daily load  >  rolling features  >  overload 3 days ahead", "d", 11))
    return b


def cp_lru():
    labels = ["HEAD", "k=7", "k=3", "k=1", "TAIL"]
    b = []
    for i, l in enumerate(labels):
        x = 20 + i * 82
        cls = "box dash" if l in ("HEAD", "TAIL") else "box"
        b.append(f'<rect class="{cls}" x="{x}" y="70" width="64" height="30"/>')
        b.append(T(x + 32, 90, l, "d" if l in ("HEAD", "TAIL") else "t", 12, "middle"))
        if i < 4:
            b.append(f'<path class="ar" d="M{x + 64} 82H{x + 82}" marker-start="url(#ar)" marker-end="url(#ar)"/>')
    b.append(f'<rect x="102" y="70" width="64" height="30" fill="none" stroke="{LM}" stroke-width="1.6" class="pulse"/>')
    b.append(T(134, 62, "just used: front", "l", 11, "middle"))
    b.append(f'<path class="ar dash" d="M348 104V122H348" stroke="{DIM}"/>' + T(348, 120, "evict", "d", 11, "middle"))
    b.append(T(18, 142, "hash map index  +  doubly linked list  +  a lock", "d", 11))
    return b


def cp_drowsy():
    b = []
    ys, x, d = [], 18, "M18 78"
    # eye aspect ratio: blinks, then one prolonged closure
    seq = [(40, 0), (6, 22), (30, 0), (6, 22), (50, 0), (96, 40), (50, 0)]
    for dx, dip in seq:
        d += f" h{dx}" if not dip else f" l{dx / 4:.0f} {dip} h{dx / 2:.0f} l{dx / 4:.0f} {-dip}"
    b.append(f'<path class="ln dash" d="M18 104H{CW - 18}"/>' + T(CW - 18, 98, "eye-closed threshold", "d", 11, "end"))
    b.append(reveal("rv", 0, 50, CW, 80, f'<path class="sc" d="{d}" style="stroke-width:2"/>', 2.6, 0.3))
    b.append(f'<circle class="l pulse" cx="198" cy="118" r="5"/>' + T(198, 104, "alert", "l", 11, "middle"))
    b.append(T(18, 142, "webcam  >  eye aspect ratio  >  alert on prolonged closure", "d", 11))
    return b


def checkpoints():
    card("scilens", 1, "research agent", "SciLens pipeline",
         "Four paper sources feed an extraction step, then a critic that loops back to targeted re-search before a gap is reported.", cp_scilens())
    card("opd", 2, "forecasting", "Hospital OPD forecasting",
         "Illustrative: daily hospital load rising toward an overload threshold, with a three-day-ahead question marker.", cp_opd())
    card("lru", 3, "systems", "LRU cache",
         "A doubly linked list between HEAD and TAIL; the most recently used key sits at the front, the tail is evicted.", cp_lru())
    card("drowsiness", 4, "computer vision", "Drowsiness detection",
         "Illustrative eye aspect ratio signal: short blinks, then one prolonged closure below the threshold triggers an alert.", cp_drowsy())


if __name__ == "__main__":
    hero(); checkpoints()
