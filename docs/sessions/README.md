# Session log

Chronological record of what was changed in this repo, why, and who decided. One markdown file per working session, date-prefixed for sortability (`YYYY-MM-DD-short-slug.md`).

## Why this exists

The plan docs (`docs/plan.md`, `docs/dashboard_plan.md`) describe *where we're going*. The session log describes *how we got here* — the decisions we made, the alternatives we rejected, and the recovery from missteps. This matters because the project has an LLM-agent collaborator (Xiaoxia) who works asynchronously and needs durable context she can read herself, not chat scrollback she can't see.

## What goes in a session log entry

Each file should answer four questions:

1. **What did we set out to do?** — one or two sentences of intent.
2. **What landed?** — the concrete artifacts (commits, files, deploys).
3. **What did we decide and why?** — the design choices, especially trade-offs and rejected alternatives. Cross-link to the relevant plan doc for full context rather than restating it here.
4. **What's still open?** — the follow-ups, dependencies, and known issues.

Keep entries concise but specific. A future reader should be able to skim a session log and know whether they need to read the linked plan docs and commits.

## Naming

`YYYY-MM-DD-short-slug.md`. If multiple sessions land on the same day, append `-2`, `-3`, etc.
