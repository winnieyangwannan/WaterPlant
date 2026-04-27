# 2026-04-27 — Plant 2 added: Fernando the Boston Fern (+ canonical add-plant runbook)

**Authors:** Winnie (driving + naming + approvals), Claude via Cowork (planning + edits)
**Outcome:** Plant 2 (Fernando, *Nephrolepis exaltata*) joins the WaterPlant household with a full profile, simulated time-series data, cartoon avatar, and per-plant detail page. The protocol used to add him is now pinned at [`docs/runbooks/add-plant.md`](../runbooks/add-plant.md) so future plants follow the same path.

## What we set out to do

Add Winnie's Boston fern as plant 2 to validate that the D7 pipeline scales beyond Goldie. Concretely: (a) generate Fernando's cartoon avatar following the "preserve plant, reinvent pot" rule, (b) build the same data-rich detail page Goldie has but with Boston-fern-appropriate care tips and a more frequent watering cadence in the simulated history, (c) drop him into the garden index alongside Goldie, and (d) capture the whole protocol as a reusable runbook so adding plant 3, 4, … becomes a checklist follow.

## What landed

### Sprite generation — Fernando v1, one-shot

The "preserve plant / reinvent pot" rule (set during Goldie's iteration) worked first try this time — the prompt explicitly called out preserving the long arching pinnate fronds, cascading habit, and bright fresh-green color while replacing the photo's plain black plastic pot with an artistic terracotta clay pot in warm rust-orange tones. Outcome: `dashboard_preview/sprites/2.png` (web, 280×384, 96 KB) + `2_original.png` (full-res, 864×1184, 1.2 MB). No iteration needed — confirms the rule pays off when the prompt frontloads it.

### `plants/2.yaml`

Full profile mirroring Goldie's structure. Care tips hand-written for Boston ferns specifically (consistent moisture, high humidity, no direct sun, tip-browning sensitivity). `sensor_idx: 1`, `pump_idx: 1`. `sprite:` block with the preserve list + chosen artistic pot ("warm rust-orange terracotta with subtle decorative band"). Photo manifest references `plants/2_fernando.HEIC` (committed).

### `plants/_sensor_map.yaml`

Updated to add `1: 2 # sensor_idx 1 -> Fernando`.

### `dashboard_preview/2.html`

Per-plant detail page modeled on `1.html`. Same animated chart (SVG with draw-on + post-pump markers) but regenerated with **seven** watering events over 30 days instead of Goldie's three — Boston ferns drink more often. Watering history table shows ten events back to mid-March. Care tips block pulls Fernando's four keys. Hero photo placeholder + photo timeline (4 simulated thumbnails + 1 hero slot). New "← Back to garden" link in the top corner since there are now multiple plants and navigation matters more.

### `dashboard_preview/index.html`

Garden scene now hosts both plants:
- Goldie repositioned to `left: 22%; top: 88%`
- Fernando added at `left: 75%; top: 88%`
- Empty plot moved back-center (`left: 50%; top: 78%`, scaled to 78%) — visually suggests "there's room for more, in the back of the garden"
- Xiaoxia repositioned to `left: 48%; top: 96%` so she sits in the foreground between the two plants
- Stat strip updated: 2 plants tracked / 50% avg moisture / 3d ago Fernando / 2 of 2 sensors online
- Plant directory grew a Fernando entry
- Header summary: "2 plants tracked · all sensors healthy"

### `docs/runbooks/add-plant.md` (new file)

The canonical protocol. Ten numbered steps from "gather inputs from the user" through "commit + push", with copy-paste commands and cross-references to `prompts/sprites.md` and the session-log template. Includes a table of required user inputs (photo, name, species, sensor index, pump index, artistic pot direction). Explicitly calls out what the runbook does *not* do (auto-generate care tips, wire firmware, run `gen_sprites.py` — those are gated on other phases).

### Cross-links

- `docs/plan.md` "Where to find things" table grew an "Adding a new plant to the garden" row pointing at the runbook.
- `docs/dashboard_plan.md` "When adding a new plant" paragraph now points at the runbook as the canonical protocol.
- The empty-plot link in the garden index now points at the runbook on GitHub instead of a placeholder anchor.

## What we decided and why

- **Name = Fernando.** Picked from a single-shot suggestion. Pun on "fern", friendly tone, mirrors Goldie's playful character. *Why this matters in the runbook:* future plant naming should aim for cute personifications, not just "the Monstera" or species names. Easy to rename in YAML if the user disagrees.
- **One-shot sprite generation, not the two-step pattern.** Goldie needed a v3 → v5 pot edit because the photo's pot was so dominant in the first generation. Fernando's prompt baked the artistic pot direction in upfront and got it right first try. The two-step pattern in `prompts/sprites.md` is now framed as a *fallback* for when one-shot fails, not the default. *Why:* one-shot is half the cost (~$0.04 vs ~$0.08) and faster.
- **Boston-fern-tuned simulated chart.** Fernando's chart shows seven watering events instead of Goldie's three, with a higher baseline (~75% post-water vs Goldie's ~70%) and shorter dry-down cycles. *Why:* the simulated data is the user-facing story of "what does this plant's life look like" — getting it wrong (e.g. a fern watered weekly) would mislead. The chart values are computed in a small Python helper in the session and pasted into the SVG; this stays manual until D3b/D4 wire real data.
- **Empty plot kept (in back-center) rather than removed.** With two plants, a single forward-comp slot is still useful as both an affordance and a visual hint that the garden is extensible. Putting it smaller and further back lets it suggest "there's more depth here" without competing with the named plants. *Why:* the alternative — drop the empty plot once the garden is "real" — would mean the next plant addition has no visible affordance.
- **Runbook lives at `docs/runbooks/add-plant.md`, not in `dashboard_plan.md`.** The runbook is operational (a checklist you follow); the plan docs are architectural (what we're building and why). Mixing them muddies both. *Why:* if future Xiaoxia / Claude / human is doing an add-plant, they want a clean checklist, not to skim through architecture decisions to find the next step.
- **Care tips hand-written, not LLM-generated.** `prompts/care_tips.md` is still pending. Hand-writing Fernando's tips is fine for now and matches Goldie's path. *Why:* hand-written tips are correct enough for a fern we've Googled care for; a flawed template-generated set would be worse than a hand-written one in the short term. The template can be added in a separate session and Fernando's tips can be regenerated from it later.

## What's still open

- **`prompts/care_tips.md`** still not pinned. When written, both Goldie's and Fernando's tips can be regenerated through it for consistency.
- **`server/gen_sprites.py`** still not implemented. Sprite generation is currently a manual Python snippet — the runbook cross-references it. Once the script lands, the runbook's Step 5 collapses to one command.
- **No real photo for Fernando in `dashboard_preview/photos/2/hero.jpg`.** The page's hero block shows the fallback emoji + "Hero photo" placeholder. Same situation as Goldie at this point. Drop a JPEG at the indicated path to populate.
- **Hardware Phase 2** still paused (relay wiring, no-pump test). Until it ships, the moisture / watering data on Fernando's page (and Goldie's) is simulated.
- **Multi-plant firmware support** (the `SENSORS[]` array change in `WaterPlant/config.h` described in `dashboard_plan.md` § "Required Arduino changes") not yet implemented. Fernando's `sensor_idx: 1` is forward-comp metadata; once Hardware Phase 2 lands, the firmware needs the second sensor entry before any real readings flow for him.
- **Commit + push.** This session's diff is unstaged. Suggested commit:

  ```
  git add plants/2.yaml plants/2_fernando.HEIC plants/_sensor_map.yaml \
          dashboard_preview/index.html dashboard_preview/2.html \
          dashboard_preview/sprites/2.png dashboard_preview/sprites/2_original.png \
          docs/runbooks/add-plant.md \
          docs/plan.md docs/dashboard_plan.md \
          docs/sessions/2026-04-27-add-plant-2-fernando.md
  git commit -m "add plant 2: Fernando (Nephrolepis exaltata) + add-plant runbook"
  git push
  ```
