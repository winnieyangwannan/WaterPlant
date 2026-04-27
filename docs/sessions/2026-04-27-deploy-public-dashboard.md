# 2026-04-27 — Public dashboard deployment + recovery from stub commits

**Authors:** Winnie (driving), Claude via Cowork (planning + edits)
**Commits:** [`6522aca`](../../) (recovery), [`47d1e85`](../../) (deploy)
**Outcome:** Goldie's styled dashboard live at `https://winnieyangwannan.github.io/WaterPlant/`

## What we set out to do

Take the styled `dashboard_preview/1.html` we'd built earlier and publish it as a real GitHub Pages site, with a plant-index landing page that's forward-compatible for adding more plants. While doing it, recover from a previous Xiaoxia commit that had unintentionally replaced production files with stubs.

## What landed

### Commit 1 — `6522aca` (recovery)

A single corrective commit on top of `46de27b`:

- **Restored Arduino firmware** from `0db2bf2`: `WaterPlant.ino`, `config.h` (calibrated `SENSOR_DRY=458` / `SENSOR_WET=265` from Phase 1), `moisture.h`, `pump.h`, `calibrate/calibrate.ino`.
- **Restored** the styled 480-line `dashboard_preview/1.html` and the original `CLAUDE.md`, `README.md`, `lesson/Openclaw_Arduino_Serial_Monitor.md`, `tests/phase1_calibration.md`, `tools/generate_diagram.py`.
- **Added `.gitignore`** covering `server/.venv/`, `__pycache__/`, `*.pyc`, `*.pyo`, `*.egg-info/`, `.DS_Store`, `*.log`, editor caches.
- **Untracked the Python virtualenv** at `server/.venv/` (1,141 files removed from index, files preserved on disk).
- **Untracked all `.DS_Store` files** (macOS metadata, no business in git).
- **Fixed the misleading "Dummy" comments** in `server/schema.sql` (also fixed `#` → `--` for proper SQL syntax) and `server/requirements.txt` (added `Jinja2>=3.1` since `render.py` imports it).
- **Updated `docs/dashboard_plan.md`** with the deployment-surface section, the two-HTML-surfaces explanation, a rules-of-the-road subsection for Xiaoxia (six explicit rules with reasons), the updated file layout, the D3a/D3b phase split, and four new entries under "Decisions resolved".

### Commit 2 — `47d1e85` (deploy)

- **`dashboard_preview/index.html`** — plant index page. Same botanical palette, animated background leaves, dark-mode-aware. One card for Goldie linking to `1.html`; a dashed "+ add another plant" placeholder for forward-compat. Hover effects, sway animations on emoji.
- **`.github/workflows/deploy.yml`** — replaced Xiaoxia's `gh-pages`-branch flow with the modern Pages flow: `actions/checkout@v4` → `actions/configure-pages@v5` → `actions/upload-pages-artifact@v3` (path: `./dashboard_preview`) → `actions/deploy-pages@v4`. Concurrency guard so redundant deploys cancel.

## What we decided and why

The full reasoning lives in [`docs/dashboard_plan.md` decisions #5–#8](../dashboard_plan.md#decisions-resolved). Quick summary:

- **Modern Pages flow** instead of the gh-pages branch approach Xiaoxia started — simpler, no orphan-checkout bugs, handles subdirectories correctly.
- **`dashboard_preview/` as the published surface**, not the `render.py`-generated pages on the VPS. The VPS pages need a live SQLite DB which CI runners don't have. The two surfaces will eventually converge (D6); for now, simulated/snapshot data baked into the HTML is fine because there's no real sensor data yet.
- **Plant-index landing page** (rather than redirecting `/` straight to Goldie's page) so adding plant 2 is a card append, not a routing rewrite.
- **Two corrective commits** (recovery + deploy) instead of one — separable for clean review and revertable independently if either has issues.
- **Recovery via `git checkout 0db2bf2 -- <files>`** rather than `git revert` — the affected files were complete replacements, not partial edits, so a checkout is cleaner than a three-way merge.

## What's still open

- **One-time Pages setup**: repo → Settings → Pages → Source: **GitHub Actions**. After that, every push to `main` redeploys.
- **Optional cleanup of orphaned scripts** — `server/generate_static_site.py` and `server/daily_reading.py` both have hardcoded paths to `/home/clawd/WaterPlant/` (the VPS) and were what made Xiaoxia's old workflow fail in CI. They're now bypassed by the new workflow but still in the repo. `render.py` already covers the rendering job. Worth removing in a follow-up.
- **Convergence between the public preview and the live VPS dashboard** (D6) — deferred until hardware Phase 2 lands and real sensor data starts flowing through `logger.py` into SQLite. Plan: snapshot the live page contents into `dashboard_preview/` periodically (or have `render.py` emit two outputs).
- **Hardware Phase 2** itself is still pending (relay wiring + no-pump bench test). When it ships, the logger daemon can start writing real readings to SQLite on the VPS, and `render.py` starts generating live pages.

## For Xiaoxia

Codified into "rules of the road" in [`docs/dashboard_plan.md`](../dashboard_plan.md#rules-of-the-road-for-xiaoxia). The short version, in case this is your first read of the repo:

- **Never replace existing files with `# Dummy ... placeholder` stubs.** Files in `WaterPlant/`, `calibrate/`, `tests/`, `lesson/`, `docs/`, and `dashboard_preview/` are real production artifacts.
- **Never commit `server/.venv/`** — it's in `.gitignore` for a reason.
- **Edit plant metadata only via `plants/<id>.yaml`** — never write `plants/_sensor_map.yaml` by hand.
- **Time-series data (`readings`, `watering_events` in SQLite) is the logger's lane.** Don't insert from anywhere else.
- **Real comments only in real code.** No "Dummy" headers on files with actual content.
- **The styled `dashboard_preview/1.html` is production for the public Pages site.** Keep it visually in sync with `server/templates/plant.html.j2`.
