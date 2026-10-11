# Setup

## Install
1. Create a **public** repo named exactly `ananyamarghade` on GitHub.
2. Copy everything into its root, **including the hidden `.github/` folder** (it holds the auto-update workflow). Push to `main`.
3. In the repo, open **Settings > Actions > General > Workflow permissions** and make sure *Read and write permissions* is selected (the workflow also requests `contents: write` itself, but an org/repo policy can override it).
4. Open the **Actions** tab, choose *refresh-profile*, and click **Run workflow** once to confirm it works.

## Automatic updates
`.github/workflows/update.yml` runs daily (03:17 UTC), on manual trigger, and whenever `scripts/` changes. It:
1. runs `fetch_activity.py` (public contribution calendar, followers, repo list and languages),
2. runs `build.py` (regenerates every SVG for both themes),
3. commits `data/` and `assets/` only if something changed.

Refreshed automatically: the weekly contribution curve in the hero and its snapshot date.
Edited by hand: README text, project list, the hero's typed lines and the four checkpoint visuals (in `scripts/generate_dashboard.py`). After editing a generator script, push it and the workflow rebuilds the assets.

Caveats: the fetch script parses public GitHub HTML, so a GitHub markup change would make the run fail (you'd see a red run in Actions and the old data would stay in place). GitHub may pause scheduled workflows in repos with no recent activity; use *Run workflow* to resume. I could not run the workflow itself in my sandbox, so it is untested until its first run on GitHub.

## Light and dark themes
Every graphic is built twice (`assets/dark/`, `assets/light/`) and the README uses `<picture>` with `prefers-color-scheme` so GitHub shows the matching one. Each SVG also carries its own background, so it stays legible even where `<picture>` is not honoured.

## Local use
```bash
python3 scripts/fetch_activity.py   # refresh data/activity.json
python3 scripts/build.py            # rebuild both themes
python3 scripts/validate.py         # add --online to check external links
```

## Data provenance
- **Fetched live:** contributions, active days, followers, repo list and primary languages.
- **From project READMEs (I did not read source code):** project descriptions. OPD metrics (ROC-AUC ≈ 0.81 etc.) are self-reported in that repo's README.
- No invented stars, hours, proficiency bars, achievements, email or LinkedIn.

## Left out
Project Aasha (design stage only) and SenentialAI (empty README) are not featured. FraudShield, VitalCare, NSCLC Digital Twin and similar had no public repo. The SciLens live demo link was dropped because it could not be verified from the build sandbox; re-add it if it is live.

## Validation status
`scripts/validate.py` passes (local files, SVG well-formedness, anchors, alt text). Not verified: the Action's first run, animation and light/dark switching on GitHub, phone layout.
