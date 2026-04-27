# Runbook — Adding a new plant to the garden

The protocol for adding a plant to the WaterPlant household. Follow these
steps in order. Tested 2026-04-27 with Goldie (id 1) and Fernando (id 2).

This runbook is **the single source of truth** for the workflow. If
anything in here gets out of sync with reality, fix the runbook in the
same commit that fixes the code. Xiaoxia (LLM agent collaborator) reads
this directly.

> **Cross-references:** sprite prompt template is at
> [`prompts/sprites.md`](../../prompts/sprites.md). The two plan docs
> (`docs/plan.md`, `docs/dashboard_plan.md`) point here. The session log
> ([`docs/sessions/`](../sessions/)) records each instance.

---

## Inputs you need from the user

Gather these *before* writing any files. Don't infer them silently — if a
field is unclear, ask.

| Field | Example | Notes |
|---|---|---|
| Photo | `IMG_0437.HEIC` | Well-lit, whole plant visible. HEIC, JPG, or PNG. |
| Name | `Fernando` | Plant's personal name (the user's choice; suggest one if asked). |
| Species | `Nephrolepis exaltata (Boston Fern)` | Common name + Latin. Identify from the photo if not given. |
| Sensor index | `1` | Which Arduino analog pin slot (`SENSORS[]` in firmware). Goldie = 0, plant 2 = 1, etc. Lives in the auto-generated [`plants/_sensor_map.yaml`](../../plants/_sensor_map.yaml). |
| Pump index | `1` (or `null`) | Which relay slot. `null` if this plant shares Goldie's pump or has none. |
| Artistic pot direction | `terracotta with carvings` | The pot in the cartoon — **does NOT need to match the real pot**. See `prompts/sprites.md` § "preserve plant, reinvent pot". |

If you haven't been told the species, identify it from the photo and
confirm with the user. A Pothos vs. a Philodendron vs. a Monstera matter
for the care-tip generator and for which sprite prompt details you'll fill in.

---

## Step 1 — Pick the new plant id

The id is the next free integer in `plants/`:

```bash
ls plants/*.yaml | grep -E '/[0-9]+\.yaml$' | sort -V
```

If `plants/1.yaml`, `plants/2.yaml` exist, the new plant is id `3`.

---

## Step 2 — Copy the reference photo into the repo

```bash
cp <source-photo> plants/<id>_<short-name>.HEIC
# e.g. plants/2_fernando.HEIC
```

Naming convention: `<id>_<short-name>.<ext>`. The id-prefix keeps
chronological + alphabetical order aligned and avoids name collisions if
two plants ever share a common name.

If the photo is HEIC, also generate a JPEG copy under `outputs/` so
Gemini can ingest it (the API accepts JPEG/PNG; HEIC needs conversion via
`pillow-heif`). See `prompts/sprites.md` for the conversion snippet.

---

## Step 3 — Create `plants/<id>.yaml`

Use [`plants/1.yaml`](../../plants/1.yaml) as the canonical template. Required keys:

```yaml
id: <int>
name: <string>
species: <Common name (Latin name)>
sensor_idx: <int>
pump_idx: <int|null>
added_at: <YYYY-MM-DD>

# Plant cartoon-sprite generation inputs (see prompts/sprites.md)
sprite:
  reference_photo: plants/<id>_<short-name>.HEIC
  output: dashboard_preview/sprites/<id>.png
  preserve: |
    - <feature 1: leaf shape>
    - <feature 2: variegation / color>
    - <feature 3: growth habit>
    - <feature 4: distinctive details>
  real_pot: "<short description of pot in the photo>"
  artistic_pot: |
    <one or two sentences describing the artistic pot we want in the cartoon>

# 4 keys — generated once, edited freely. See prompts/care_tips.md (planned).
care_tips:
  watering: <one or two sentences>
  sunlight: <...>
  soil: <...>
  temperature: <...>

# Each photo: file path on the VPS, taken_at date, optional caption, is_hero flag.
photos:
  - path: <id>/<YYYY-MM-DD>_hero.jpg
    taken_at: <YYYY-MM-DD>
    caption: <free-text>
    is_hero: true

# Newest first. Added by Xiaoxia when the user mentions plant events.
notes:
  - date: <YYYY-MM-DD>
    body: <free-text>
```

---

## Step 4 — Regenerate `plants/_sensor_map.yaml`

The sensor map is auto-derived from the individual `plants/<id>.yaml`
files (per the rules-of-the-road in [`docs/dashboard_plan.md`](../dashboard_plan.md#rules-of-the-road-for-xiaoxia)).
Do not edit it by hand. Once `server/render.py --rebuild-sensor-map` is
wired, that's the command. Until then, the file is small enough to update
manually — but always derive it from the YAMLs, never the other way around.

---

## Step 5 — Generate the cartoon sprite

Follow the **two-step pattern** documented in [`prompts/sprites.md`](../../prompts/sprites.md):

1. **Generate from photo** — call Gemini 2.5 Flash Image with the photo as
   image input + the full prompt template (`{{species}}`, `{{preserve_features}}`,
   `{{real_pot_description}}`, `{{artistic_pot_description}}` substituted from the
   YAML's `sprite:` block). Save as `dashboard_preview/sprites/<id>_v1.png`.
2. **Edit just the pot** (only if the first generation didn't get the pot right).
   Pass `<id>_v1.png` back in with the focused edit prompt. Save as `<id>_v2.png`.
3. **Post-process** — chroma-key to transparent + downscale:

   ```bash
   cd dashboard_preview/sprites
   convert <id>_v<final>.png -fuzz 12% -transparent white <id>_original.png
   convert <id>_original.png -resize 384x384 -strip <id>.png
   ```

4. **Clean up** the intermediate `<id>_v1.png`, `<id>_v2.png` once
   `<id>.png` and `<id>_original.png` are committed.

Cost: ~$0.04 per generation × however many iterations (typically 2).

---

## Step 6 — Create `dashboard_preview/<id>.html` (per-plant detail page)

Copy [`dashboard_preview/1.html`](../../dashboard_preview/1.html) as the
template. Substitute:

- `<title>` and any visible references to the previous plant's name and species.
- The hero `<img src="photos/...">` reference if one exists.
- The simulated data baked into the page: 30 days of moisture readings,
  recent watering events with before/after %, photo timeline, notes log.
  All of it is currently inline in the HTML; replace with this plant's
  values. (Once D1/D3b are live, this stops being simulated and gets
  rendered from SQLite by `server/render.py`.)
- The care-tip block (4 keys) — pull from the YAML.

> **Heads-up:** until `server/render.py` is wired into the live VPS
> rendering path (D3b), `dashboard_preview/<id>.html` is a hand-edited
> static file. It WILL drift from the YAML if both are edited
> independently. The YAML is the source of truth for metadata; the HTML
> is the source of truth for layout. When in doubt, regenerate the HTML
> from the YAML.

---

## Step 7 — Wire the new plant into the garden index

Edit [`dashboard_preview/index.html`](../../dashboard_preview/index.html):

1. **Add a `.plant-<name>` CSS rule** with the plant's position in the
   garden scene (`left: <%>; top: <%>`). Goldie is at `left: 28%; top: 88%`.
   Spread plants out so they don't overlap.
2. **Add the plant's `<a class="plant ...">` block** inside the `.garden`
   section. Reference the sprite at `sprites/<id>.png` and link to `<id>.html`.
3. **Move or remove the empty plot** if it now collides with the new
   plant's position. As long as there's at least one open spot in the
   garden, keep the empty plot as a hint for the next add-plant.
4. **Update the stat-strip** at the bottom of the scene: plants tracked
   count, average moisture, last-watered.
5. **Update the plant directory** (`.plant-list`) with a new `<li>`.
6. **Update the header summary** ("N plants tracked · all sensors healthy").

---

## Step 8 — Verify

```bash
# HTML well-formedness
python3 -c "from html.parser import HTMLParser; ..."
# Sprite paths exist
ls dashboard_preview/sprites/<id>.png dashboard_preview/sprites/<id>_original.png
# Local preview
open dashboard_preview/index.html  # or click the file in Cowork
```

Confirm visually that the new plant appears in the garden, hover/click
work, and the per-plant page (`<id>.html`) renders without console errors.

---

## Step 9 — Update `plan.md` status snapshot + write a session log

- Bump the plant count anywhere `plan.md` mentions "N plants".
- Add a session-log entry under [`docs/sessions/`](../sessions/) following
  the [session-log template](../sessions/README.md). One entry per
  add-plant event so the audit trail of "when did Bertha join the
  household" is durable.

---

## Step 10 — Commit + push

```bash
git add plants/<id>.yaml plants/<id>_<short-name>.HEIC plants/_sensor_map.yaml \
        dashboard_preview/<id>.html dashboard_preview/index.html \
        dashboard_preview/sprites/<id>.png dashboard_preview/sprites/<id>_original.png \
        docs/sessions/<date>-add-plant-<id>-<short-name>.md \
        docs/plan.md
git commit -m "add plant <id>: <Name> (<Latin species name>)"
git push
```

GitHub Pages republishes within a minute or two.

---

## What this runbook intentionally does *not* do

- Generate care tips with an LLM. That belongs to the (still pending)
  `prompts/care_tips.md` template — see [`docs/dashboard_plan.md`
  § care-tip prompt template](../dashboard_plan.md#the-care-tip-prompt-template).
  For now, hand-write care tips or copy from a reliable source.
- Wire the plant into real sensor data. That's the hardware track —
  `SENSORS[]` in `WaterPlant/config.h` needs the corresponding entry, and
  hardware Phase 2/3 need to be live for actual readings to flow.
- Run `server/gen_sprites.py`. That script doesn't exist yet (planned
  in D7c). Until it lands, sprite generation is a manual Python snippet
  per `prompts/sprites.md`.

---

## Changelog

- **2026-04-27** — runbook created. Validated by adding plant 2
  (Fernando, Boston Fern) following these exact steps.
