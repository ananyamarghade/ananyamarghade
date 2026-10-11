#!/usr/bin/env python3
"""Builds every SVG for both themes (assets/dark and assets/light)."""
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
for theme in ("dark", "light"):
    for script in ("generate_assets.py", "generate_dashboard.py"):
        subprocess.run([sys.executable, str(HERE / script)], check=True, cwd=HERE,
                       env={**os.environ, "THEME": theme}, stdout=subprocess.DEVNULL)
    print(f"built {theme}")
