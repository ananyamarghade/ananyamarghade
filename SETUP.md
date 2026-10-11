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

Refreshed automatically: repo count, contribution total, heatmap, monthly chart, language chart, followers, snapshot dates, identity-panel stats.
Edited by hand: the identity text (role, focus, languages), project cards and captions, toolkit map, README prose. After editing a generator script, push it and the workflow rebuilds the assets.

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

## Left out (no public repo or evidence found)
FraudShield, VitalCare, NSCLC Digital Twin, dyslexia platform, VitaTrace, achievements/research. Send links or summaries to add them.

## Fix before publishing
- SenentialAI needs a README; its repo name seems to contain a typo ("Senential"), used verbatim so links work.
- Confirm the two CSVs in the OPD repo are public-licensed and free of patient identifiers.
- Add LinkedIn/email to Contact if you want them public.

## Validation status
Done: `validate.py` (234 checks passed: local files, both theme folders match, SVG well-formedness, anchors, alt text, secret-like strings, sizes); static renders of the dark and light artwork with CairoSVG, which does not run CSS animation.
**Not done, please check on GitHub:** the Action's first run; that animations play through GitHub's image proxy (the static state is complete if not); that GitHub switches to the light images in light mode; phone layout (diagram text is 12-13 px and shrinks on phones, so each graphic has alt text and the identity panel has a plain-text version).
