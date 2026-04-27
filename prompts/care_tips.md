# Care-tips prompt template (pinned)

Every plant in the WaterPlant household has a `care_tips:` block in its
`plants/<id>.yaml` with **exactly four keys**: `watering`, `sunlight`,
`soil`, `temperature`. Those four keys also drive the "Care tips" section
on the plant's detail page (`dashboard_preview/<id>.html`), so the contract
is **structural, not just stylistic** — if a key is missing or extra, the
page renderer breaks.

This file pins the prompt that any collaborator (Claude, Xiaoxia, Winnie)
uses to generate that block from a species name. Pinning it ensures:

- Two Monsteras get tips in the **same shape** (same four keys, same length,
  same tone), regardless of who generated them or when.
- Tightening or loosening the format (e.g. adding a `fertilizer` key, dropping
  `temperature`) is a **one-file change** that propagates to every future plant.
- The renderer's contract stays stable across plant additions.

> **Cross-references:** add-plant runbook at
> [`docs/runbooks/add-plant.md`](../docs/runbooks/add-plant.md) Step 3.
> Sprite prompt template at [`prompts/sprites.md`](sprites.md). Plant YAMLs at
> [`plants/`](../plants/).

---

## Inputs you need before generating

1. **Species name** — common name + Latin name, e.g.
   `Golden Pothos (Epipremnum aureum)`. The LLM uses both: the common name
   anchors the tone, the Latin name disambiguates (e.g. *Sansevieria
   trifasciata* vs. *Sansevieria cylindrica* — different watering needs).
2. **(Optional) Personalization** — if the user has a specific environment
   note worth pinning (e.g. "kept in a north-facing window", "next to a
   heating vent"), pass it through. The base prompt is generic; environment
   notes go into the user-turn message after the species line.

---

## The contract (do not weaken)

The output **must** be:

- **Exactly four keys** in this order: `watering`, `sunlight`, `soil`,
  `temperature`. No `fertilizer`, no `humidity`, no extras. Adding new keys
  is a separate change to this template (and every existing YAML).
- **Each value is one or two short sentences** (~20–40 words). Long enough
  to be specific, short enough to glance at on the detail page.
- **Practical, concrete, no marketing fluff.** "Bright, indirect light" is
  good. "Loves to bask in the gentle morning sun" is not.
- **Plain-English imperatives or descriptions**, not bullet lists or
  numbered steps. The detail page renders each value as a single sentence
  block.
- **Output as a YAML fragment**, ready to paste under the plant's `name`,
  `species`, `sensor_idx` etc. block. **No code fences, no preamble, no
  trailing commentary.** Just:

  ```
  care_tips:
    watering: "..."
    sunlight: "..."
    soil: "..."
    temperature: "..."
  ```

  This is parsed and merged programmatically — extra text breaks the parse.

---

## The system prompt (constant)

Use this verbatim as the system message in any LLM call. It tells the
model what shape to produce and which failure modes to avoid:

> You are filling in the `care_tips:` block for a new houseplant being
> added to a home plant-monitoring system. Your output is parsed as YAML
> and rendered directly on the plant's profile page, so the format is
> strict.
>
> Output ONLY a YAML fragment with EXACTLY these four keys, in this order:
> `watering`, `sunlight`, `soil`, `temperature`.
>
> Each value is a string in double quotes, one or two short sentences
> (~20–40 words), practical and concrete. No bullet points, no headers,
> no preamble, no code fences, no trailing commentary.
>
> Tone: warm and clear, like a knowledgeable friend giving advice to
> another plant owner. Specific where it matters (frequency, light type,
> soil ingredients, temperature range), without being marketing-y.
>
> Failure modes to avoid:
> - Adding extra keys (humidity, fertilizer, pruning, etc.) — only the four.
> - Removing or reordering keys.
> - Wrapping the output in code fences.
> - Hedging ("usually", "in some cases") instead of giving a clear default.
> - Long paragraphs. One or two sentences per key.

---

## Few-shot examples (constant)

Pass these as previous-turn user/assistant pairs so the model has concrete
shape to imitate. The Monstera example anchors a third species; Goldie
and Fernando are the household's actual plants, included so the model
picks up the exact tone the project already uses.

### Example 1 — Monstera deliciosa

**User:**
```
Generate care tips for: Monstera deliciosa (Swiss Cheese Plant)
```

**Assistant:**
```
care_tips:
  watering: "Water when the top 2 in of soil is dry — usually weekly in summer, every 10–14 days in winter. Tolerates a missed week better than soggy roots."
  sunlight: "Bright, indirect light. Tolerates lower light but produces fewer fenestrations. Direct afternoon sun scorches the leaves."
  soil: "Well-draining mix: peat, perlite, and bark in roughly equal parts. Repot every 2–3 years when roots circle the bottom."
  temperature: "65–85°F (18–29°C). Avoid cold drafts below 55°F and dry heating vents in winter."
```

### Example 2 — Golden Pothos (plant 1: Goldie)

**User:**
```
Generate care tips for: Epipremnum aureum (Golden Pothos)
```

**Assistant:**
```
care_tips:
  watering: "Let the top 1–2 in of soil dry out completely between waterings — typically every 7–10 days. Pothos prefers slight underwatering to overwatering and droops as a clear signal when thirsty."
  sunlight: "Bright, indirect light. Tolerates lower light but loses variegation. Avoid direct sun, which scorches leaves and bleaches the yellow."
  soil: "Well-draining indoor potting mix with perlite. Doesn't mind being slightly root-bound — repot every 2–3 years."
  temperature: "65–85°F (18–29°C). Avoid cold drafts below 50°F and dry heating vents in winter."
```

### Example 3 — Boston Fern (plant 2: Fernando)

**User:**
```
Generate care tips for: Nephrolepis exaltata (Boston Fern)
```

**Assistant:**
```
care_tips:
  watering: "Keep soil consistently moist — water every 3–5 days, never let it dry out completely. Boston ferns drop fronds fast when underwatered. Bottom-water occasionally to keep the root ball evenly hydrated."
  sunlight: "Bright, indirect light. Direct sun will scorch the fronds. Tolerates lower light but grows slower; rotate weekly so all sides stay full."
  soil: "Rich, well-draining potting mix with extra peat or coco coir for moisture retention. Slightly acidic (pH 5.5–6.5). Repot every 2 years or when roots fill the pot."
  temperature: "60–75°F (16–24°C), with humidity above 50%. Mist daily or use a humidifier during winter heating — dry air browns the leaflet tips."
```

---

## How to invoke (current path — manual)

Until `server/gen_care_tips.py` lands (planned alongside `gen_sprites.py`
in D7c-adjacent work), generation is a one-off Python snippet against the
Gemini text endpoint. The pattern:

```python
import json, os, urllib.request

key = os.environ["GEMINI_API_KEY"]   # loaded from .env
species = "Sansevieria trifasciata (Snake Plant)"  # whatever the new plant is

system_prompt = """You are filling in the `care_tips:` block for a new houseplant being
added to a home plant-monitoring system. Your output is parsed as YAML
and rendered directly on the plant's profile page, so the format is
strict.

Output ONLY a YAML fragment with EXACTLY these four keys, in this order:
watering, sunlight, soil, temperature.

Each value is a string in double quotes, one or two short sentences
(~20-40 words), practical and concrete. No bullet points, no headers,
no preamble, no code fences, no trailing commentary.

Tone: warm and clear, like a knowledgeable friend giving advice to
another plant owner. Specific where it matters (frequency, light type,
soil ingredients, temperature range), without being marketing-y.

Failure modes to avoid:
- Adding extra keys (humidity, fertilizer, pruning, etc.) - only the four.
- Removing or reordering keys.
- Wrapping the output in code fences.
- Hedging ("usually", "in some cases") instead of giving a clear default.
- Long paragraphs. One or two sentences per key.
"""

# Paste the three few-shots verbatim from this file, as alternating
# user / assistant turns. Then the new species as the final user turn.
contents = [
    {"role": "user",  "parts": [{"text": "Generate care tips for: Monstera deliciosa (Swiss Cheese Plant)"}]},
    {"role": "model", "parts": [{"text": '''care_tips:
  watering: "Water when the top 2 in of soil is dry - usually weekly in summer, every 10-14 days in winter. Tolerates a missed week better than soggy roots."
  sunlight: "Bright, indirect light. Tolerates lower light but produces fewer fenestrations. Direct afternoon sun scorches the leaves."
  soil: "Well-draining mix: peat, perlite, and bark in roughly equal parts. Repot every 2-3 years when roots circle the bottom."
  temperature: "65-85F (18-29C). Avoid cold drafts below 55F and dry heating vents in winter."'''}]},
    # ... (Goldie + Fernando few-shots — copy from the examples above) ...
    {"role": "user",  "parts": [{"text": f"Generate care tips for: {species}"}]},
]

url = ("https://generativelanguage.googleapis.com/v1beta/models/"
       "gemini-2.5-flash:generateContent?key=" + key)
body = json.dumps({
    "systemInstruction": {"parts": [{"text": system_prompt}]},
    "contents": contents,
}).encode()
req = urllib.request.Request(
    url, data=body, headers={"Content-Type": "application/json"}, method="POST"
)
with urllib.request.urlopen(req, timeout=30) as r:
    d = json.loads(r.read())

print(d["candidates"][0]["content"]["parts"][0]["text"])
# Paste the output into plants/<id>.yaml under the existing keys.
```

Cost: free-tier (text generation has nonzero free-tier quota on Gemini —
unlike image generation). Iterate freely.

After pasting the output into `plants/<id>.yaml`, **glance at the result
before committing.** The model is good but not infallible: a Sansevieria
that gets watered "every 5–7 days" instead of "every 2–3 weeks" would be
a real problem. Two failure modes to watch for:

- **Wrong frequency.** Look up the plant if you don't know it.
- **Generic stand-in care.** If the model doesn't recognize the species,
  it sometimes falls back to "moderate water, bright light, well-draining
  soil" for everything. That's a sign the species name was ambiguous —
  add the Latin name and retry.

---

## Future automation

When `server/gen_care_tips.py` is added (alongside `gen_sprites.py` in
D7c-adjacent work), it will:

1. Take a plant id as argument.
2. Read `species` from `plants/<id>.yaml`.
3. Call Gemini with this template's prompt + few-shots.
4. Parse the response as YAML, validate the four-key contract.
5. Patch `plants/<id>.yaml`'s `care_tips:` block in place.

At that point the runbook's "fill in care_tips" step collapses to:

```
python server/gen_care_tips.py <id>
```

Until then, paste-and-glance is the workflow.

---

## Changelog

- **2026-04-27** — file created. Four-key contract pinned. System prompt,
  failure-mode guard rails, and three few-shots (Monstera, Goldie,
  Fernando) committed. Goldie's and Fernando's existing care tips were
  hand-written; they may be regenerated through this template later for
  consistency, but only if the regenerated versions land on the same or
  better quality.
