#!/usr/bin/env python3
"""Regenerates every SVG in ../assets. Pure standard library.

Usage:  python3 scripts/generate_assets.py

Design rules baked in:
  * Base (un-animated) state of every element is its FINISHED state, so if a
    renderer ignores CSS animation the image still looks complete.
  * `prefers-reduced-motion` switches all animation off.
  * System fonts only (no external requests).
"""
import math
import os
import pathlib
from html import escape as E

THEME = os.environ.get("THEME", "dark")  # "dark" or "light"; scripts/build.py runs both
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / THEME
OUT.mkdir(parents=True, exist_ok=True)

if THEME == "light":
    BG, PANEL, RULE = "#fbfbf9", "#ffffff", "#cfd8dc"
    TXT, DIM, CY, LM = "#14181b", "#566168", "#0f766e", "#4d7c0f"
    LEVELS = ["#e8edef", "#a8ddd6", "#5cbfb4", CY, LM]
else:
    BG, PANEL, RULE = "#0b0d0e", "#111517", "#26343a"
    TXT, DIM, CY, LM = "#e8e6df", "#8a979b", "#4fd1c5", "#b8e63c"
    LEVELS = ["#161c1f", "#1f5d59", "#2f9b93", CY, LM]

CSS = """
text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace}
.serif{font-family:Georgia,"Times New Roman",serif}
.t{fill:@TXT}.d{fill:@DIM}.c{fill:@CY}.l{fill:@LM}
.ln{fill:none;stroke:@RULE;stroke-width:1}
.ar{fill:none;stroke:@DIM;stroke-width:1.4}
.sc{fill:none;stroke:@CY;stroke-width:2;stroke-linejoin:round}
.box{fill:@PANEL;stroke:@RULE;stroke-width:1.2}
.dash{stroke-dasharray:5 4}
.flow{fill:none;stroke:@CY;stroke-width:2.4;stroke-linecap:round;stroke-dasharray:8 92;animation:flow 3.4s linear infinite}
.lm{stroke:@LM}
.pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.6s ease-in-out infinite}
.ty{transform-box:fill-box;transform-origin:left center;animation:type 2.2s steps(28) both}
.grow{transform-box:fill-box;transform-origin:left center;animation:grow 1.1s ease-out both}
@keyframes flow{from{stroke-dashoffset:8}to{stroke-dashoffset:-92}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
@keyframes type{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""
for k, v in {"@TXT": TXT, "@DIM": DIM, "@CY": CY, "@LM": LM, "@RULE": RULE, "@PANEL": PANEL}.items():
    CSS = CSS.replace(k, v)

MARKER = (f'<marker id="ar" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" '
          f'orient="auto-start-reverse"><path d="M0 0L8 4L0 8z" fill="{DIM}"/></marker>')


def svg(name, w, h, title, desc, body, bg=True):
    bgrect = f'<rect width="{w}" height="{h}" fill="{BG}"/>' if bg else ""
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'role="img" aria-labelledby="t d">\n<title id="t">{E(title)}</title>\n<desc id="d">{E(desc)}</desc>\n'
           f'<style>{CSS}</style>\n<defs>{MARKER}</defs>\n{bgrect}\n{body}\n</svg>\n')
    (OUT / name).write_text(doc, encoding="utf-8")
    print(f"wrote assets/{name} ({len(doc)/1024:.1f} KB)")


def T(x, y, s, cls="d", size=13, anchor="start", extra=""):
    return f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" text-anchor="{anchor}" {extra}>{E(s)}</text>'


def box(x, y, w, h, label, dashed=False, cls="t", size=13):
    c = "box dash" if dashed else "box"
    return (f'<rect class="{c}" x="{x}" y="{y}" width="{w}" height="{h}"/>'
            f'<text x="{x + w/2}" y="{y + h/2 + 4.5}" class="{cls}" font-size="{size}" text-anchor="middle">{E(label)}</text>')


def flow(d, lm=False, delay=0.0, dash=None):
    cls = "flow lm" if lm else "flow"
    st = f"animation-delay:{delay}s;" + (f"stroke-dasharray:{dash};" if dash else "")
    return f'<path class="{cls}" pathLength="100" d="{d}" style="{st}"/>'


def ecg(x0, x1, y, step):
    d, x = f"M{x0} {y}", x0
    while x + step <= x1:
        d += f" h{step - 35} l6 -6 l6 12 l7 -26 l8 41.6 l8 -21.6"
        x += step
    return d + f" H{x1}"


# --------------------------------------------------------------------- hero
def hero():
    W, H = 900, 300
    b = [f'<pattern id="g" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" class="ln"/></pattern>',
         f'<rect width="{W}" height="{H}" fill="url(#g)" opacity=".35"/>']
    b.append(f'<path class="ln" d="M48 58H852"/>')
    b.append(T(48, 40, "~/ananyamarghade", "d", 14))
    b.append(f'<circle class="l pulse" cx="684" cy="35" r="4"/>')
    b.append(T(852, 40, "ai, software, data", "d", 14, "end"))
    # network (right), scaled down into a compact block
    layers = [(590, [120, 200, 280]), (690, [90, 160, 230, 300]), (790, [120, 200, 280]), (868, [200])]
    g = ['<g transform="translate(240 24) scale(.7)">']
    for (xa, ya), (xb, yb) in zip(layers, layers[1:]):
        for y1 in ya:
            for y2 in yb:
                g.append(f'<path class="ln" d="M{xa} {y1}L{xb} {y2}"/>')
    chains = [([(590, 200), (690, 160), (790, 200), (868, 200)], False, 0),
              ([(590, 120), (690, 230), (790, 280), (868, 200)], True, 1.1),
              ([(590, 280), (690, 90), (790, 120), (868, 200)], False, 2.2)]
    for pts, lm, dl in chains:
        g.append(flow("M" + "L".join(f"{x} {y}" for x, y in pts), lm, dl))
    for i, (x, ys) in enumerate(layers):
        for j, y in enumerate(ys):
            if (i, j) in [(1, 1), (2, 2), (0, 0)]:
                g.append(f'<circle class="l pulse" cx="{x}" cy="{y}" r="6" style="animation-delay:{(i + j) * 0.4}s"/>')
            else:
                g.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{PANEL}" stroke="{CY}" stroke-width="1.6"/>')
    g.append('</g>')
    b += g
    b.append(T(653, 250, "data  >  model  >  decision", "d", 12))
    # title
    b.append(f'<text class="serif t" x="44" y="132" font-size="70">Ananya</text>')
    b.append(f'<text class="serif t" x="44" y="200" font-size="70">Marghade<tspan class="l">.</tspan></text>')
    # typed statements
    lines = ["B.Tech CSE, AI & Data Science", "agents, forecasting, decision support"]
    for i, s in enumerate(lines):
        y = 232 + i * 26
        cid = f"c{i}"
        b.append(f'<clipPath id="{cid}"><rect class="ty" x="48" y="{y - 19}" width="520" height="26" '
                 f'style="animation-delay:{0.5 + i * 2.4}s;animation-timing-function:steps({len(s)})"/></clipPath>')
        b.append(f'<g clip-path="url(#{cid})"><text x="48" y="{y}" class="d" font-size="16">&gt;&gt; </text>'
                 f'<text x="76" y="{y}" class="t" font-size="16">{E(s)}</text></g>')
    d = ecg(48, 852, 288, 160)
    b.append(f'<path class="ln" d="{d}"/>')
    b.append(flow(d, False, 0, "14 86"))
    svg("hero.svg", W, H, "Ananya Marghade, profile header",
        "Header with the name Ananya Marghade, two typed lines (B.Tech CSE with AI and Data Science; agents, "
        "forecasting and decision support), a small animated neural-network graph and a signal trace along the bottom.",
        "\n".join(b))


# ------------------------------------------------------------------ divider
def divider():
    b = [f'<path class="ln" d="M0 18H900"/>']
    for x in range(0, 900, 20):
        h = 6 if x % 100 == 0 else 3
        b.append(f'<path class="ln" d="M{x} {18 - h}V{18 + h}"/>')
    b.append(flow("M0 18H900", False, 0, "4 96"))
    b.append(f'<rect class="l pulse" x="446" y="14" width="8" height="8" transform="rotate(45 450 18)"/>')
    svg("divider.svg", 900, 36, "Section divider", "A thin ruled line with tick marks and a moving signal pulse.", "\n".join(b))


# -------------------------------------------------------------------- cards
def card(fn, kind, name_lines, status, stack_lines, title, desc, body):
    w, h = 900, 300
    chip_w = len(status) * 7.4 + 22
    b = [f'<rect x=".5" y=".5" width="899" height="299" fill="{BG}" stroke="{RULE}"/>',
         f'<path class="ln" d="M310 30V270"/>',
         T(40, 52, kind, "d", 14)]
    for i, n in enumerate(name_lines):
        b.append(f'<text class="serif t" x="40" y="{104 + i * 40}" font-size="34">{E(n)}</text>')
    b.append(f'<rect x="40" y="184" width="{chip_w:.0f}" height="26" fill="none" stroke="{LM}" stroke-opacity=".7"/>')
    b.append(T(51, 201, status, "l", 12))
    for i, s in enumerate(stack_lines):
        b.append(T(40, 244 + i * 20, s, "d", 13))
    b.append(body)
    svg(fn, w, h, title, desc, "\n".join(b))


def scilens():
    b = [f'<path class="ln" d="M384 82H816"/>', flow("M384 82H816")]
    labels = ["search", "extract", "landscape", "gaps", "critic"]
    for i, l in enumerate(labels):
        x = 340 + i * 108
        b.append(f'<path class="ln" d="M{x + 44} 82V96"/>')
        b.append(box(x, 96, 88, 44, l, cls="t"))
        if i < 4:
            b.append(f'<path class="ar" d="M{x + 90} 118H{x + 106}" marker-end="url(#ar)"/>')
    loop = "M816 140V196H384V140"
    b.append(f'<path class="ar dash" d="{loop}" marker-end="url(#ar)"/>')
    b.append(flow(loop, True, 1.2))
    b.append(T(600, 220, "investigator re-searches until validated or capped", "d", 13, "middle"))
    b.append(T(856, 256, "validated gaps  >  research proposal", "c", 13, "end"))
    card("project-scilens.svg", "research agent", ["SciLens"], "live demo linked",
         ["Python, FastAPI, LangGraph", "OpenAlex, arXiv, CrossRef"],
         "SciLens pipeline diagram",
         "Five stages (search, extract, landscape, gaps, critic) with a feedback loop from the evidence critic back "
         "to targeted re-search, ending in a research proposal export.", "\n".join(b))


def opd():
    pts = []
    for i in range(21):
        v = 30 + 22 * math.sin(i * 0.55) + 14 * math.sin(i * 1.7 + 1) + i * 2.2
        pts.append((340 + i * 18, max(72, min(212, 214 - v))))
    d = "M" + "L".join(f"{x} {y:.0f}" for x, y in pts)
    b = [f'<rect x="700" y="60" width="160" height="170" fill="{CY}" fill-opacity=".07" stroke="{RULE}" class="dash"/>',
         f'<path class="ln" d="M340 230H860"/>',
         f'<path d="M340 100H860" stroke="{LM}" stroke-opacity=".7" stroke-dasharray="4 5" fill="none"/>',
         T(344, 92, "overload threshold", "l", 12),
         f'<path class="sc" d="{d}"/>', flow(d, False, 0, "6 94"),
         f'<path d="M700 {pts[-1][1]:.0f}C760 {pts[-1][1]:.0f} 800 100 860 100" fill="none" stroke="{CY}" '
         f'stroke-opacity=".6" stroke-dasharray="4 5"/>',
         f'<path class="ar" d="M700 60V230"/>',
         f'<circle cx="860" cy="100" r="6" fill="none" stroke="{LM}" stroke-width="2" class="pulse"/>',
         T(846, 84, "?", "l", 18, "end"),
         T(700, 250, "t", "t", 13, "middle"), T(860, 250, "t + 3 days", "t", 13, "end"),
         T(340, 276, "illustrative shape, not project data", "d", 12)]
    card("project-opd-warning.svg", "forecasting", ["Hospital OPD", "Early Warning"], "ml pipeline",
         ["Python, Random Forest", "time-based split"],
         "OPD early warning diagram",
         "A line of daily hospital load up to today (t), a shaded three-day horizon, and an open question marker on "
         "the overload threshold at t plus three days. The curve is illustrative, not project data.", "\n".join(b))


def lru():
    b = [box(340, 84, 100, 104, "", False),
         T(390, 112, "HashMap", "t", 13, "middle"), T(390, 132, "key > node", "d", 12, "middle"),
         T(390, 170, "O(1)", "l", 14, "middle")]
    xs = [480, 558, 636, 714, 792]
    labels = ["HEAD", "k=3", "k=1", "k=7", "TAIL"]
    for i, (x, l) in enumerate(zip(xs, labels)):
        b.append(box(x, 112, 58, 46, l, dashed=i in (0, 4), cls="d" if i in (0, 4) else "t"))
        if i < 4:
            b.append(f'<path class="ar" d="M{x + 60} 135H{x + 78}" marker-start="url(#ar)" marker-end="url(#ar)"/>')
    arc = "M743 112C743 58 587 58 587 112"
    b += [f'<path class="ar dash" d="{arc}" marker-end="url(#ar)"/>', flow(arc, True),
          T(665, 50, "get(k): move to front", "c", 12, "middle"),
          T(587, 182, "most recent", "d", 12, "middle"),
          f'<path class="ar" d="M743 190V164" marker-end="url(#ar)"/>',
          T(743, 206, "evict here", "l", 12, "middle"),
          f'<path class="ar dash" d="M390 188V232H667V158" marker-end="url(#ar)"/>',
          T(528, 252, "lookup jumps straight to the node", "d", 12, "middle"),
          T(340, 284, "get() takes the write lock because it reorders the list", "d", 12)]
    card("project-lru-cache.svg", "concurrency", ["Thread-safe", "LRU cache"], "java + design doc",
         ["HashMap + doubly linked list", "ReentrantReadWriteLock"],
         "LRU cache structure diagram",
         "A hash map pointing into a doubly linked list between HEAD and TAIL sentinels. Accessed keys move to the "
         "front, and the least recently used node at the tail is evicted.", "\n".join(b))


def aasha():
    b = [f'<rect class="box dash" x="328" y="64" width="500" height="140" fill="none"/>',
         T(344, 88, "on device, offline-first (proposed)", "d", 12)]
    for i, l in enumerate(["voice", "symptoms", "triage", "records"]):
        x = 344 + i * 124
        b.append(box(x, 112, 100, 56, l, dashed=True))
        if i < 3:
            b.append(f'<path class="ar" d="M{x + 102} 140H{x + 122}" marker-end="url(#ar)"/>')
    b += [f'<path class="ln" d="M394 186H766"/>', flow("M394 186H766"),
          T(340, 238, "decision support only; it does not diagnose", "t", 13),
          T(340, 262, "the repository holds design documents, not an app", "d", 12)]
    card("project-aasha.svg", "healthcare design", ["Project", "Aasha"], "design stage",
         ["voice-first, offline-first", "for ASHA and ANM workers"],
         "Project Aasha concept diagram",
         "Dashed boxes mark a proposed on-device flow: voice input, symptom analysis, triage and records, with a note "
         "that the tool is decision support only and the repository contains design documents.", "\n".join(b))


def sentinel():
    b = [f'<path class="ln" d="M386 82H810"/>', flow("M386 82H810")]
    for i, l in enumerate(["analyze", "dashboard", "history", "reports", "settings"]):
        x = 340 + i * 106
        b.append(f'<path class="ln" d="M{x + 46} 82V92"/>')
        b.append(box(x, 92, 92, 44, l))
    b += [f'<path class="ln" d="M386 136V164H810V136"/>',
          f'<path class="ar dash" d="M580 164V184" marker-end="url(#ar)"/>',
          f'<path class="box" d="M526 196V230A54 10 0 0 0 634 230V196"/>',
          f'<ellipse class="box" cx="580" cy="196" rx="54" ry="10"/>',
          T(580, 221, "Supabase", "t", 12, "middle"),
          T(656, 218, "supabase/migrations", "d", 12),
          T(340, 276, "README is empty; behaviour is not described here", "d", 12)]
    card("project-senentialai.svg", "web app", ["SenentialAI"], "web app, undocumented",
         ["Next.js, TypeScript", "Tailwind, Supabase"],
         "SenentialAI app structure diagram",
         "Five app sections (analyze, dashboard, history, reports, settings) connected to a Supabase database, "
         "drawn from the repository structure.", "\n".join(b))


# ---------------------------------------------------------------- languages
def languages():
    rows = [("Python", 4), ("no language", 3), ("Java", 2), ("HTML", 2), ("C", 1), ("TypeScript", 1),
            ("Jupyter Notebook", 1), ("PL/SQL", 1), ("Assembly", 1), ("Lex", 1)]
    assert sum(n for _, n in rows) == 17
    b = [f'<text class="serif t" x="40" y="50" font-size="26">Primary language per public repository</text>',
         T(40, 74, "17 public repositories, snapshot 2026-10-11, from github.com", "d", 13)]
    for i, (l, n) in enumerate(rows):
        y = 112 + i * 26
        op = "1" if i == 0 else ".55"
        b.append(T(40, y + 11, l, "t", 14))
        b.append(f'<rect class="grow" x="210" y="{y}" width="{n * 70}" height="14" fill="{CY}" fill-opacity="{op}" '
                 f'style="animation-delay:{i * 0.1:.1f}s"/>')
        b.append(T(210 + n * 70 + 10, y + 12, str(n), "c", 14))
    for i, s in enumerate(["counts repositories,", "not skill or hours.", "labs, coursework and team", "projects are all included.",
                           "'no language' means docs", "or design-only repos."]):
        b.append(T(580, 130 + i * 24, s, "d", 13))
    svg("repo-languages.svg", 900, 390, "Primary language per public repository",
        "Bar chart of 17 public repositories by primary language: Python 4, no language detected 3, Java 2, HTML 2, "
        "and one each of C, TypeScript, Jupyter Notebook, PL/SQL, Assembly and Lex.", "\n".join(b))


# ------------------------------------------------------------------ closing
def closing():
    d = ecg(40, 700, 90, 220)
    b = [f'<path class="ln" d="{d}"/>', flow(d, False, 0, "14 86"),
         f'<path class="ln" d="M700 90H860"/>',
         f'<circle class="l pulse" cx="700" cy="90" r="6"/>',
         T(40, 156, "end of profile", "d", 13), T(860, 156, "thanks for reading the source", "d", 13, "end")]
    svg("closing.svg", 900, 180, "End of profile",
        "A signal trace that settles into a flat line with a pulsing marker, captioned end of profile.", "\n".join(b))


if __name__ == "__main__":
    hero()
