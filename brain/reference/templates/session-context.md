---
type: session-context
session_id: <ses_...>
project: <project-name>
date: <YYYY-MM-DD>
updated: <ISO timestamp>
status: active
tags: [session-context]
---

# Session Context — <project>

## Cached Files
| file-path | mtime+size | tokens | summary |
|-----------|------------|--------|---------|
| <path>    | <mtime>+<size> | <N> | ≤2-line summary |

## Delta Log (append-only)
- <HH:MM> — <file> <added|updated|removed>
- 14:30 — docs/style.md updated
- 14:45 — docs/brain/decisions/auth-strategy.md added

## Contract
Main agent writes this cache; subagents read it and never write it. Original files stay source of truth — this cache never shadows them.
