# 2026-04-27 — D7 v1: emoji garden index

**Authors:** Winnie (driving + design decisions), Claude via Cowork (planning + edits)
**Outcome:** `dashboard_preview/index.html` replaced by an "open garden" scene. Emoji used as placeholder sprites; custom pixel art deferred to D7c.

## What we set out to do

Make the public index page more fun. Inspiration: a pixel-art "headquarters" UI where AI agents live in rooms in a shared building. Translated to this project: a digital *garden* where each plant has a cartoon avatar, **Xiaoxia walks around as a small lobster**, and per-plant health is shown visually so the page tells you "Goldie is thirsty" at a glance.

## What landed

### `dashboard_preview/index.html` — full rewrite

- Open garden scene (16:9, gradient sky → grass) replacing the previous cards grid.
- Sky decorations: rotating sun (🌞), three drifting clouds (☁️), a bird crossing the horizon (🐦).
- Ground decorations: scattered flowers (🌸 🌷 🌼), grass tufts (🌾), rocks (🪨).
- **Goldie** at left ground-level: 🪴 with a hover label showing name + moisture.
- **Empty plot** at right: brown CSS-trapezoid pot with a `+`, labelled "add a plant", forward-comp for plant 2. Links to the `# adding a plant` anchor on the README.
- **Xiaoxia the lobster** (🦞) centered between them, gently wiggling. Hover her for a thought bubble ("All plants healthy today 🦞").
- Below the scene: a 4-tile stat strip (plants tracked / avg moisture / last watered / sensor health) and a plain-text plant directory. The directory exists as accessible fallback for keyboard / screen-reader users and (eventually) narrow viewports.
- Dark mode and `prefers-reduced-motion` both respected. Site-wide warm-cream palette preserved.
- Plant detail page (`1.html`) **untouched** — separate concern.

### `docs/dashboard_plan.md`

New **D7** section added covering: locked-in design (open garden, lobster Xiaoxia, floating-icon health indicators, static-first animation, no mobile fallback), v1 emoji-as-sprite mapping, deferred D7b (event-driven motion) and D7c (real Gemini-generated pixel sprites). Six new entries (#9–#15) under "Decisions resolved 2026-04-27".

### `docs/plan.md`

Status table grew three rows: **D7** (active), **D7b** (deferred until real readings flow), **D7c** (deferred until Google Cloud billing is enabled).

### `.gitignore` / `.env` / `.env.example`

`.env` (containing `GEMINI_API_KEY`) added to repo root and gitignored. `.env.example` checked in as a template. `.gitignore` extended with `.env`, `.env.*`, `!.env.example`.

## What we decided and why

Full reasoning in [`docs/dashboard_plan.md` decisions #9–#15](../dashboard_plan.md#2026-04-27-visual-polish--d7-design). Quick summary:

- **Open garden, not rooms grid.** All plants in one shared scene — gives Xiaoxia somewhere to walk later (D7b), scales to ~10 plants for one household, matches the inspiration screenshot's vibe better than a tiled grid would.
- **Xiaoxia is a literal lobster (🦞).** Visual joke matches the playful name; reads instantly; distinctive against green plants. Considered "lab-coat scientist" briefly, dropped because lobster is more memorable and stays cute when she's "watering" a plant in D7b.
- **Floating icons over sprite-pose changes.** v1 ships with one sprite per plant, plus three floating badge emojis (💧 thirsty / ✨ just-watered / ⚠️ offline). Pose swaps require multiple sprites per plant — deferred to D7b once we know the design is right.
- **Static first.** No walking, no watering animation in v1. Cheaper, ships now, and lets us see if the design holds up before committing to motion work.
- **Emoji as placeholder sprites.** The original plan was to generate custom pixel art via Gemini 2.5 Flash Image (nanobanana). The user's API key works for text but the image model has free-tier quota = 0 — needs Google Cloud billing. Rather than block on that, v1 uses Unicode emoji at 64–96 px. The migration path is a single CSS swap once the sprite library exists.
- **No mobile fallback.** An open garden doesn't compress gracefully into 360 px. Punted to a later phase. The plain-text plant directory below the scene is the de-facto narrow-screen view for now.
- **API key handling.** Key was pasted in chat; saved to `.env` (gitignored) on the user's machine. Rotation recommended after this project to avoid lingering exposure in conversation logs.

## What's still open

- **Commit + push.** This session's edits (`dashboard_preview/index.html`, `docs/dashboard_plan.md`, `docs/plan.md`, `.gitignore`, `.env.example`) are unstaged. The `.env` file is intentionally not staged. Once committed and pushed, the existing `.github/workflows/deploy.yml` will republish to GitHub Pages.
- **D7c — real pixel sprites.** Gated on enabling billing on the Google Cloud project tied to the API key (~$0.04/image, ~$1.20 for the v1 library). Once unblocked: author `prompts/sprites.md` with one prompt per asset, add `server/gen_sprites.py`, generate and commit PNGs under `dashboard_preview/sprites/`, swap the emoji spans for `<img>` tags or a CSS `background-image`.
- **D7b — event-driven motion.** Gated on D1/D3b being live (real sensor data flowing). Then: Xiaoxia walks to whichever plant just got a reading, watering animation on `PUMP_ON`, plant sprite swaps to droopy when moisture < threshold.
- **Mobile design.** A separate mini-phase whenever it matters; probably a list view below a 720 px breakpoint replacing the garden scene.
- **Hardware Phase 2** (relay wiring, no-pump test) still paused before D1/D3b can light up real data.
