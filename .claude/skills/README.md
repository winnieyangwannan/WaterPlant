# Skills

Custom slash commands for this project. Each `.md` file here becomes a `/skill-name` command in Claude Code.

## Structure

```
.claude/
  skills/
    example.md   → /example
```

## Skill File Format

```markdown
---
description: One-line description shown in /help
---

Prompt content here. Describe what Claude should do when this skill is invoked.
```
