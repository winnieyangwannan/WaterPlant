# Plant cartoon sprite prompts (pinned)

Every plant in the WaterPlant garden gets a cartoon avatar generated via
Google's **Gemini 2.5 Flash Image** (model `gemini-2.5-flash-image`, a.k.a.
nanobanana) using the real photograph as image-to-image input. This file is
the **single source of truth** for those prompts so every plant comes back
in a coherent style.

The garden index (`dashboard_preview/index.html`) renders these sprites in
place of the placeholder emoji once a plant has one. Sprites are committed
to `dashboard_preview/sprites/<id>.png`.

> **Why this file exists:** without a pinned template, asking on Tuesday
> vs. Friday, or asking via Winnie vs. Xiaoxia, would yield differently
> styled outputs. The garden would feel like a collage. Pinning the style
> guide + rule + template here keeps the look coherent forever.

---

## Inputs you need before generating

1. **A real photograph of the plant** — any common format. HEIC works after
   converting to JPEG (see "How to invoke" below). The photo should be
   well-lit and show the whole plant.
2. **The plant's species** — common name + Latin name, e.g.
   `Golden Pothos (Epipremnum aureum)`.
3. **A `sprite:` block in `plants/<id>.yaml`** with two free-text fields:
   - `preserve` — a short, specific list of features to copy from the photo
     (leaf shape, variegation pattern, growth habit, distinctive features).
   - `pot` — the artistic pot direction. The real pot is irrelevant; pick
     something that fits the plant.

Goldie's `sprite:` block is the canonical example — see `plants/1.yaml`.

---

## The core rule: PRESERVE the plant, REINVENT the pot

This is the most important convention in this whole file. Every prompt
must explicitly call out which features to preserve and which to replace.

**Preserve faithfully from the photo:**
- Leaf shape
- Variegation pattern, color distribution
- Growth habit (cascading, upright, climbing, bushy, etc.)
- Overall proportions
- Any distinctive features (long trailing vines, leaf damage, particular
  markings)

**Replace — DO NOT copy from photo:**
- **The pot.** Real household pots are usually plain plastic or
  utilitarian. Use an artistic pot regardless: a hand-woven wicker basket
  in warm tan tones, hand-painted ceramic, decorative terracotta with
  carvings, etc. Make it look like a polished mobile-game collectible.
- **The background.** Plain white only — no kitchen, no scenery, no
  shelves, no other objects.

**Why:** the plant carries the identity ("that's Goldie"); the pot is just
the frame. A polished artistic pot makes the avatar feel like a finished
mobile-game collectible rather than a literal photo trace. Confirmed by
Winnie 2026-04-27 after rejecting a faithful-to-photo plain black pot in
favor of a wicker basket.

---

## Style guide (constant across all plants)

These bullets go into every prompt verbatim — do not vary them per plant.

- Vibrant **mobile-game cartoon illustration** (Stardew Valley meets Plant
  Tycoon).
- **Bold black outlines** on every leaf, stem, and pot detail.
- **Soft cel-shaded coloring** with subtle highlights and shadow gradients.
- **Saturated, vibrant colors.**
- Centered composition, the entire plant fully visible, slight
  three-quarter angle.
- Plain white background, no scenery, no text, no UI elements.
- Add subtle natural character: a few small brown speckles on a couple of
  leaves.

---

## Prompt template

Fill in the four `{{ ... }}` fields from the plant's YAML. The rest is
constant.

```
Transform this real photograph of a {{species}} houseplant into a vibrant
mobile-game cartoon illustration of the SAME PLANT.

PRESERVE FAITHFULLY from the photo:
{{preserve_features}}

REPLACE — DO NOT copy from photo:
- The pot. The real photo shows {{real_pot_description}}. Do NOT use that.
  Instead use {{artistic_pot_description}}. Make it feel like a polished
  mobile-game collectible asset.
- Background. No scenery. Plain white background only.

STYLE: bold black outlines on every leaf, stem, and pot detail. Soft
cel-shaded coloring with subtle highlights and shadow gradients. Saturated
vibrant colors. Polished mobile-game collectible aesthetic (Stardew Valley
meets Plant Tycoon). Add subtle natural character: a few small brown
speckles on a couple of leaves.

Centered composition, the entire plant fully visible. No text, no UI
elements.
```

---

## Worked example — Goldie (plant id 1)

Substitutions (from `plants/1.yaml` `sprite:` block):

- `species` → `Golden Pothos (Epipremnum aureum)`
- `preserve_features`:
  - Exact heart-shaped leaf shape
  - Dramatic green-and-yellow marbled variegation with prominent bold
    yellow patches across many leaves (the "golden" in golden pothos)
  - Cascading downward growth habit, leaves trailing well below the pot
  - Many large lush leaves spilling out, mix of fully green leaves and
    heavily yellow-variegated leaves
- `real_pot_description` → `a plain black plastic pot`
- `artistic_pot_description` → `a beautiful hand-woven wicker basket in
  warm tan-and-cream tones, with clearly visible woven texture, a braided
  rim at the top, and subtle shadow/highlight detail`

**Process actually used (2026-04-27)** — this is the canonical pattern,
not the single-shot version:

1. Convert `plants/goldie.HEIC` → `outputs/goldie_real.jpg` (1024 px, JPEG).
2. **Step 1 — generate from photo** with the full prompt above + the
   substitutions listed. Output saved as `goldie_v3.png`. Plant came out
   beautifully variegated and shaped like the real Goldie. Pot copied from
   the photo (plain black plastic) — wrong.
3. **Step 2 — edit just the pot** by passing `goldie_v3.png` back in as
   input with the focused edit prompt (see "Two-step edit" section above).
   Output saved as `goldie_v5.png`. Plant identical to v3; pot now a
   wicker basket.
4. **Post-process** (see next section): chroma-key the white background to
   transparent, save full-resolution as `1_original.png`, downscale to
   384 px wide as `1.png`.

---

## Generation pattern: one-shot vs. two-step edit

**The single-shot prompt above gets 80–90% of the way there.** From experience
in the 2026-04-27 session that produced Goldie's avatar, the failure modes
are predictable:

- The model sometimes mutes the variegation or growth habit when it's
  also being asked to invent the pot.
- The model sometimes copies the real pot (or guesses something
  utilitarian) when the prompt is too short.

**The two-step "generate then edit-pot" pattern is the reliable path** when
the first generation gets the plant right but the pot wrong (or vice
versa). It's what produced Goldie's final v5:

1. **Generate from the photo** with the full prompt above. Save as
   `<id>_v1.png`. If the plant looks right *and* the pot looks right,
   you're done — promote it.
2. If the plant is right but the pot is wrong, **do a second image-to-image
   pass using `<id>_v1.png` as input** with a focused edit prompt:

   > Edit this cartoon illustration. Make ONE change only: replace the
   > [current pot description] with [target artistic pot description].
   > DO NOT CHANGE anything else — keep every leaf in exactly the same
   > position with the same shape, the same variegation, the same
   > cascading habit, the same composition, the same outline style, and
   > the same plain white background. Only the pot changes.

   The strict "ONE change only" + "DO NOT CHANGE" framing keeps the model
   from also rearranging leaves, which it will otherwise do.

This pattern decouples the two hard problems (faithful plant capture vs.
artistic pot invention) so each step is constrained.

## How to invoke (current path — manual)

Until `server/gen_sprites.py` lands in D7c, generation is a one-off Python
snippet. The pattern (sourced from a working session 2026-04-27):

```python
import json, base64, urllib.request, os
from pillow_heif import register_heif_opener
from PIL import Image

# 1. Convert HEIC → JPEG (skip if photo is already JPEG/PNG)
register_heif_opener()
img = Image.open("plants/goldie.HEIC")
img.thumbnail((1024, 1024))           # speed + cost
img.convert("RGB").save("plants/goldie.jpg", "JPEG", quality=88)

# 2. Build the prompt by substituting fields from plants/<id>.yaml
prompt = open("prompts/sprites.md").read()  # then format the template block
# ... (in practice, copy the template and substitute manually for now)

# 3. Call Gemini 2.5 Flash Image with image-to-image input
key = os.environ["GEMINI_API_KEY"]   # loaded from .env
img_b64 = base64.b64encode(open("plants/goldie.jpg", "rb").read()).decode()
url = (
  "https://generativelanguage.googleapis.com/v1beta/models/"
  "gemini-2.5-flash-image:generateContent?key=" + key
)
body = json.dumps({"contents": [{"parts": [
    {"inlineData": {"mimeType": "image/jpeg", "data": img_b64}},
    {"text": prompt},
]}]}).encode()
req = urllib.request.Request(
    url, data=body, headers={"Content-Type": "application/json"}, method="POST"
)
with urllib.request.urlopen(req, timeout=90) as r:
    d = json.loads(r.read())

# 4. Save the PNG
for p in d["candidates"][0]["content"]["parts"]:
    if "inlineData" in p:
        out = "dashboard_preview/sprites/<id>.png"
        open(out, "wb").write(base64.b64decode(p["inlineData"]["data"]))
```

Cost: ~$0.04 per generation. Iterate freely.

---

## Post-processing (chroma-key + downscale)

Gemini outputs an RGB PNG with a solid white background. The garden scene
needs a transparent sprite, and a sized-down PNG for fast page loads. Two
versions are committed per plant:

- `dashboard_preview/sprites/<id>_original.png` — full resolution
  (~864×1184 px), background made transparent. Kept as the source of
  record so future re-renders (different sizes, different effects)
  don't have to re-call the API.
- `dashboard_preview/sprites/<id>.png` — downscaled to ~384 px on the
  longest side, transparent. This is what the page actually loads.

ImageMagick one-liner (the same one used for Goldie):

```
cd dashboard_preview/sprites
# 1. Chroma-key white → transparent (12% fuzz handles anti-aliased edges)
convert <raw>.png -fuzz 12% -transparent white <id>_original.png
# 2. Downscale for the web
convert <id>_original.png -resize 384x384 -strip <id>.png
```

The `12%` fuzz tolerance is calibrated for Gemini's anti-aliased edges —
lower than that leaves a faint white halo on the leaves.

## Future automation (D7c)

When `server/gen_sprites.py` is added (planned in `docs/dashboard_plan.md`
§ D7c), it will:

1. Take a plant id as argument.
2. Look up the plant's photo and `sprite:` block from `plants/<id>.yaml`.
3. Substitute the four `{{ ... }}` fields into the template above.
4. Call the Gemini API.
5. Write `dashboard_preview/sprites/<id>.png` and commit.

At that point, adding a new plant becomes:

```
python server/gen_sprites.py <id>
```

…and the garden picks up the new sprite on the next page render.

---

## Changelog

- **2026-04-27** — file created. Style guide and "preserve plant /
  reinvent pot" rule pinned. Goldie's worked example added.
- **2026-04-27** — added the **two-step "generate then edit-pot"** pattern
  after discovering single-shot prompts trade off plant fidelity vs. pot
  quality; added the **post-processing** section (chroma-key + downscale,
  using ImageMagick `-fuzz 12%`); rewrote Goldie's worked example to
  reflect the actual process used (v3 → v5 → 1.png).
