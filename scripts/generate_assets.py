#!/usr/bin/env python3
"""Shared theme, CSS and SVG helpers for generate_dashboard.py. Pure standard library.

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
.blink{animation:blink 1.1s steps(1) infinite}
.fadein{animation:rise .9s ease-out both}
.seq{animation:seq 3.6s ease-in-out infinite}
.s1{animation-delay:.6s}.s2{animation-delay:1.2s}.s3{animation-delay:1.8s}
.altA{opacity:0;animation:altA 7s ease-in-out infinite}
.altB{animation:altB 7s ease-in-out infinite}
.scan{animation:scan 6s linear infinite}
.grow{transform-box:fill-box;transform-origin:left center;animation:grow 1.1s ease-out both}
@keyframes flow{from{stroke-dashoffset:8}to{stroke-dashoffset:-92}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
@keyframes type{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@keyframes seq{0%,100%{opacity:.4}15%,45%{opacity:1}}
@keyframes altA{0%,42%{opacity:1}50%,92%{opacity:0}100%{opacity:1}}
@keyframes altB{0%,42%{opacity:0}50%,92%{opacity:1}100%{opacity:0}}
@keyframes scan{from{transform:translateY(-70px)}to{transform:translateY(520px)}}
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
