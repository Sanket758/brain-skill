---
type: decision
date: 2026-08-23
project: my_project
tags: [architecture, cli-tool, config]
status: active
related:
  - "[[my_project/findings/config-contamination-bugfix|config-contamination-bugfix]]"
---

# Built a config CLI instead of hand-editing global config

## Decision
Build a dedicated CLI instead of continuing to hand-edit global config. Two structural choices:
1. **Catalog model for integrations** — global config keeps only universal entries; domain-specific
   ones live as pure JSON files in a neutral library dir and get injected into project config on demand.
2. **Library + symlink for plugins** — selective plugins live in a library dir the tool does NOT
   scan, symlinked into projects (verified empirically that the tool discovers them through symlinks).

Neutral storage root chosen deliberately: survives an uninstall of the tool
(user's explicit concern about the config dir being wiped).

## Key mechanism (verified empirically)
- `{env:VAR}` is the ONLY interpolation the tool expands in config; `$VAR` stays literal
  → secrets travel as references, real values live in a 0600 env file.

## Consequences
- New global entries should be added via the catalog command, never hand-edited
  (see the contamination incident in the related bugfix note).

## Rejected Alternatives
- **Keep hand-editing** — rejected: an earlier edit leaked domain config into the global layer.
