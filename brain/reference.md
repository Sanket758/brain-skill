# Brain Skill — Reference (loaded on demand)

Load this file only when about to write a note. For behavior contract (when to read/write), see `SKILL.md` in the same directory.

## Frontmatter Schema (mandatory)

Every note MUST have this YAML frontmatter. Agents grep on these fields — keep names stable.

```yaml
---
type: decision | finding | rejection | bugfix | constraint | performance | invariant | gotcha | playbook | map | preference | thinking | runbook | checkpoint | tooling | session-context | session-summary   # required, pick one (session-summary only for cross-project session summaries)
date: 2026-07-09                        # required, ISO date
project: experiments                    # required, the project subfolder name
tags: [auth, postgres, architecture]    # required, lower-case, kebab if multi-word
status: active | superseded | obsolete  # required, default "active"
superseded_by: ./other-note-slug.md     # only when status is superseded
related:                                # optional, wikilinks to related notes
  - "[[experiments/decisions/auth-strategy|auth-strategy]]"
---
```

## Note Types

### `decision` — durable architecture/tech choice
A choice with rationale that future sessions must respect unless explicitly superseded. Body:
```markdown
# <Descriptive title>

## Context
Why this decision was needed — one paragraph.

## Decision
What we chose. Be specific (which library, which pattern, which config).

## Rationale
Why. Multiple bullets OK. Reference concrete constraints/file paths.

## Rejected Alternatives
- **Option A** — rejected because <reason>
- **Option B** — rejected because <reason>

## Affected Code
Paths/symbols (use codegraph links if relevant). Optional.

## Open Questions
Things still undecided — list or "None."
```

### `finding` — investigation result
What was tried and what was learned. Not a decision — a record of what happened. Body:
```markdown
# <What was investigated>

## Hypothesis
What we expected to find / prove.

## Method
How it was investigated. Concrete (commands, files read, queries run).

## Result
What actually happened. Be honest about failures.

## Recommendation
Next step or `None — record only` if this is pure documentation.
```

### `rejection` — a deliberate "no"
Records a deliberate decision NOT to do something — prevents re-litigating. Same body format as `decision` but `## Decision` becomes `## Decision: do NOT do X` and the rationale is "because Y."

### `bugfix` — bug pattern + fix
Prevents re-debugging the same issue. Body:
```markdown
# <Error message or symptom>

## Symptom
What was observed (error message, incorrect behavior, stack trace excerpt).

## Root Cause
Why it happened. Be specific about the mechanism.

## Fix
What was changed to resolve it. Include file:line if possible.

## Prevention
How to avoid this in the future (tests, checks, patterns).

## First Occurrence
Date and context when this was first encountered.
```

### `constraint` — system limit
Records a hard limit discovered through testing or failure. Body:
```markdown
# <What has the constraint>

## Limit
The specific value/threshold (e.g., "batch_size > 64 causes OOM").

## Evidence
How this was discovered (command run, error message, measurement).

## Safe Value
The known-good value to use instead.

## Workaround
Alternative approach if the safe value isn't acceptable.

## Environment
System specs where this was measured (GPU, RAM, OS, versions).
```

### `performance` — benchmark data
Real measured numbers, not guesses. Body:
```markdown
# <What was measured>

## Metric
What was measured (latency, throughput, memory, etc.).

## Result
The actual numbers with units.

## Conditions
Under what conditions (dataset size, hardware, config).

## Comparison
Before/after or vs. alternative (if applicable).

## Action
What to do with this information.
```

### `invariant` — architecture rule
A "must never" or "always must" rule discovered through experience. Body:
```markdown
# <Rule description>

## Rule
The exact constraint (e.g., "Never modify src/auth/ without updating tests").

## Reason
Why this rule exists (what breaks if violated).

## Verification
How to check compliance (command, test, grep pattern).

## Last Verified
Date when this was last confirmed to hold.
```

### `gotcha` — library/API quirk
A surprise behavior in a dependency. Body:
```markdown
# <Library/version> — <Issue>

## Issue
What unexpected behavior was observed.

## Cause
Why the library behaves this way.

## Workaround
How to work around it.

## Version
Library version where this was encountered.

## Fixed In
Version where this is resolved (or "Not yet fixed").
```

### `playbook` — debugging workflow
A step-by-step approach that successfully diagnosed a class of problems. Body:
```markdown
# <Symptom class>

## Symptom
What the user/agent sees.

## Triage Steps
1. First, check <X> because <reason>
2. Then, verify <Y> by <command>
3. If <condition>, the cause is <Z>

## Common Root Causes
- **Cause A**: <description> → Fix: <action>
- **Cause B**: <description> → Fix: <action>

## Avoid
Common wrong turns that waste time.
```

### `map` — module/file responsibility
Clarifies what a module does and its boundaries. Body:
```markdown
# <Module path>

## Purpose
One-sentence description of what this module does.

## Key Exports
- `functionName()` — what it does
- `ClassName` — what it represents

## Dependencies
- Depends on: <modules/files>
- Depended on by: <modules/files>

## Boundaries
What this module should NOT do (related concerns that belong elsewhere).

## Change Triggers
When to modify this module (requirements changes, bug fixes, etc.).
```

### `thinking` — model reasoning process
Captures *how* a problem was solved, not just *what* was decided. Body:
```markdown
# <Problem description>

## Problem Statement
What was being solved — one paragraph.

## Reasoning Chain
1. **Initial hypothesis**: <what we thought first>
   - Checked: <what we looked at>
   - Result: <what we found>
2. **Second hypothesis**: <what we thought next>
   - Evidence: <supporting data>
   - Pattern match: <does this look like a known pattern?>
3. **Evaluation**:
   - Option A: <approach> → <pros/cons>
   - Option B: <approach> → <pros/cons>
4. **Conclusion**: <what we chose and why>

## What Made This Work
- Which thinking style helped (systematic, pattern-match, exploratory)
- What evidence grounded the reasoning
- What saved time

## Anti-patterns Avoided
- Traps we didn't fall into
- Rabbit holes we avoided

## Meta-Notes
- Model used: <model name>
- Time taken: <approximate duration>
- Similar problems: <links to related thinking notes>
```

### `preference` — user preference
Records how the user likes things done. Store in `~/ObsidianVault/shared/decisions/` so all projects benefit. Body:
```markdown
# <Preference topic>

## Preference
What the user prefers (specific tool, style, workflow, etc.)

## Context
When/where this applies (all projects, specific scenarios, etc.)

## Example
Concrete example of the preference in action.

## Anti-pattern
What to avoid (the opposite of the preference).

## First Recorded
Date and session where this preference was expressed.
```

### `runbook` — environment setup + how-to-run
A recipe that reproduces a working state. Answers "how do I actually run this?" — operational knowledge that is not a decision and not an investigation result. Store in `<project>/runbooks/`; create the folder with `mkdir -p` if missing. Update it when the setup changes rather than writing a second runbook. Body:
```markdown
# <What this runbook is for>

## Environment
- Paths (venv, config, data dirs)
- Ports / services / daemons
- Versions (tool, runtime, OS)

## Setup
Step-by-step commands to get a working state.

## Run
Commands to execute the main workflow.

## Verify
How to confirm it works (command + expected output).

## Gotchas
Known traps when running this (launch flags, env vars, ordering).
```

### `tooling` — agent-tooling operational fact
An operational fact about the agent's OWN tooling/environment (where the orchestrator stores state, how to query it), not about the user's app code. Cross-project: store in `~/ObsidianVault/shared/tooling/` with `project: shared`. Body:
```markdown
# <Tool name> — <operational fact>

## Tool
What tool/mechanism this is about.

## How It Works
The operational detail (where state lives, how it's queried).

## Gotchas
Traps when working with this tool.

## Last Verified
Date this was confirmed.
```

### `checkpoint` — durable project state snapshot
A dated snapshot of "where things stand right now" so a future session can resume: what's done, current focus, next steps, known blockers. Project-scoped: store in `<project>/checkpoints/`; create the folder with `mkdir -p` if missing. Distinct from `hot.md` (rolling, overwritten) and from a session summary (cross-project, user-initiated only): a checkpoint is a durable, dated snapshot that stays on file. Write one when the user says "save checkpoint", at a natural milestone, or before a long pause. Body:
```markdown
# <Checkpoint — YYYY-MM-DD>

## State
What is done / working right now (be concrete).

## Current Focus
What is actively in progress.

## Next Steps
Ordered list of what to do next.

## Blockers
Known obstacles + workarounds.

## Resume
How a future agent picks up from here (files to read, commands to run).
```

### `session-context` — session-scoped context cache
An EPHEMERAL per-session cache of files already read this session, so the main agent and its subagents don't re-read unchanged markdown context files (style guides, cv, user-preferences, mode configs, output reports). Lives at `<project>/docs/brain/session-context.md` (reachable via the `./docs/brain/` symlink — subagents share the main agent's cwd). The main agent writes it; subagents read it only. Deleted at session end — never `superseded`/`obsolete`, never written to `shared/`. Verbatim content is stored only for files ≤ 400 chars; everything else is summarized. Body:
```markdown
# Session Context — <project>

## Cached Files
| file-path | mtime+size | tokens | summary |
|-----------|------------|--------|---------|
| <path>    | <mtime>+<size> | <N> | ≤2-line summary |

## Delta Log (append-only)
- <HH:MM> — <file> <added|updated|removed>

## Contract
Main agent writes this cache; subagents read it and never write it. Original files stay source of truth — this cache never shadows them.
```

## File naming

- `kebab-case-short-slug.md` — e.g., `auth-strategy.md`, `postgres-vs-mongo.md`, `jwt-rejected.md`
- No dates in the filename (date lives in frontmatter, sortable by mtime).
- No spaces, no underscores, no capital letters in filenames.

## Wikilink convention (CRITICAL)

Obsidian resolves `[[filename]]` against ALL files in the vault. With per-project folders, generic filenames collide (`auth.md` exists in 5 projects). Always use the path-qualified form:

```
[[experiments/decisions/auth-strategy|auth-strategy]]
       ^ vault-root path         ^ display
```

- Path = vault-root-relative, no `.md` extension
- Display = short text shown in the link, your choice
- Bare `[[auth-strategy]]` is forbidden — it may silently link to the wrong project's note

### Reciprocity rule (MANDATORY)

Links must be bidirectional. If note A references note B (frontmatter `related:` or inline wikilink), note B MUST reference A back. Procedure when writing/updating a note:

1. Collect every outgoing link (new `related:` entries + inline wikilinks).
2. For each target, check whether it already links back (`grep -l "<target-slug>" docs/brain/**/<target>.md` or read its frontmatter).
3. If not, add the reverse entry to the target's `related:` list (or body where contextually appropriate).

Unidirectional links fragment the Obsidian graph and cause missed recall. Verify reciprocity before ending any vault write.

## `hot.md` format

`<project>/hot.md` is a single rolling state file. Format:

```markdown
# Hot state — <project>

Last updated: 2026-07-09

## Current focus
<one or two lines about what's actively in progress>

## Recent decisions (max 5, newest first)
- 2026-07-09 — [[experiments/decisions/auth-strategy|auth-strategy]] — switched to JWT
- 2026-07-08 — [[experiments/decisions/postgres-vs-mongo|postgres-vs-mongo]] — chose Postgres

## Open questions
- <or "None">

## Log (append-only, newest at top, max 20 lines — older entries drop off when scrolling)
- 2026-07-09 14:30 — Investigated refresh-token flow, wrote auth-strategy decision
- 2026-07-09 11:00 — Started auth migration, see finding [[experiments/findings/auth-investigation|auth-investigation]]
```

Update `Last updated:` every time you append. When the log grows past 20 lines, drop the oldest — those entries should already be captured in durable `decisions/` or `findings/` notes.

## Edge cases

### A note becomes wrong (the decision no longer applies)
Don't delete it. Set `status: superseded` and add a `superseded_by:` frontmatter field pointing to the new note (or just add a `## Superseded YYYY-MM-DD` section at the top of the body explaining what replaced it and why). Deletion hides history; supersession preserves it.

### A note is fully obsolete (the topic no longer matters at all)
Set `status: obsolete` and add a one-line `## Obsoleted YYYY-MM-DD — <reason>`. Keep the file in place — Obsidian's backlinks still point to it.

### You're unsure if an existing note covers your topic
Read the matches fully before writing. If you only have partial overlap — update the existing note with an additional `## Updated YYYY-MM-DD` section rather than splitting. A single authoritative note beats two competing half-notes.

### You want to write about a cross-project convention
Use `~/ObsidianVault/shared/`. Example: "always use biome for formatting across all my personal projects." Frontmatter still needs `project: shared`. Tooling facts about the agent's own environment go in `shared/tooling/` (type `tooling`); conventions and preferences go in `shared/decisions/`.

### Two projects share a decision
Write the canonical note in `shared/`, and write a thin pointer note in each project's `decisions/` with frontmatter `tags: [pointer]`, body a one-line `[[shared/decisions/...|...]]` link plus "see shared decision — applies to this project because <reason>". Don't duplicate the full content per-project.

### Sub-agent returns a finding worth recording
You (the main agent) write the note, crediting the sub-agent in the body: `## Source: oracle investigation, session <session-id>`. Do not let the sub-agent write directly unless the task was a long-running investigation with explicit instructions to use the vault.

### You're working in a project that doesn't yet have a `docs/brain/` symlink
Either: create the project subfolder under `~/ObsidianVault/<project-name>/` and symlink it (`ln -sfn ~/ObsidianVault/<project-name> <project-dir>/docs/brain`), OR skip the brain behavior for that session. Don't read/write the vault from arbitrary project dirs without the symlink — it muddles per-project isolation.

### The Obsidian desktop app isn't running
That's fine. Agents touch files directly. You only need Obsidian running if you (the human) want to browse the graph/view notes — the agents don't depend on it.

### Project has existing markdown corpus before brain was bootstrapped

This is the **resource-folder pattern** — typically found in projects that predate brain. Treatment:

1. IdentifyFolders that contain durable decisions / findings / context the agent needs:
   - Decide once (do not re-survey every session) and record in a brain-sidecar file: `docs/brain/.resources` — plain text, one folder per line, with a one-word role tag
   - Example file content for a project like `my-project`:
     ```
     docs/             # prior decision/architecture documents
     interview-prep/   # prior findings/interview debriefs
     data/             # operational source-of-truth (read-only)
     reports/          # per-application data (read-only)
     ```
2. On session start of a non-trivial task, after reading `hot.md`, ALSO read `docs/brain/.resources` (if present) and grep across the listed folders for the task's topic keywords. Treat those folders as **read-only context** — do NOT migrate their contents into the brain vault.
3. When you write a brain `decisions/` or `findings/` note that relates to a file in one of these resource folders, link the original via `[[folder/file|display]]` (vault-root-relative path) in the note body. Keep the citation chain greppable in both directions.
4. Never duplicate the contents of resource folders into brain notes. Brain is the **decision layer**, the existing files are the **data layer** — they remain source of truth.
5. The `.resources` file is optional. If missing, the brain's read contract defaults to grepping only `docs/brain/` itself. If a project grows a corpus over time, add the `.resources` file when the agent complains about needing more context.

### What goes in the resource folder list vs. the brain vault

| Type | Belongs in | Why |
|---|---|---|
| A new decision made this session | `docs/brain/decisions/` | Live outcome of reasoning — accumulates |
| A new finding (interview result, debugging breakthrough) | `docs/brain/findings/` | Live outcome — accumulates |
| A complex reasoning process | `docs/brain/thinking/` | Captures *how* we solved it — accumulates |
| A pre-existing architecture doc you'd cite | Resource folder (e.g., `docs/ARCHITECTURE.md`) | ALREADY a decision; brain note can link to it |
| Operational data (tables, state, pipelines) | Resource folder (e.g., `data/`) | Source of truth; don't shadow |
| Workflow definitions (skill files, mode files) | Their project-native location (e.g., `modes/`) | Define tooling, not memory |
| Per-record data (per-application reports, per-person records) | Resource folder (e.g., `reports/`) | Read-only data, not memory |

## Templates

Templates live in `reference/templates/<type>.md` — one file per type. Load only the template you need when writing.

| Type | Template File |
|------|--------------|
| decision | `reference/templates/decision.md` |
| finding | `reference/templates/finding.md` |
| bugfix | `reference/templates/bugfix.md` |
| constraint | `reference/templates/constraint.md` |
| performance | `reference/templates/performance.md` |
| invariant | `reference/templates/invariant.md` |
| gotcha | `reference/templates/gotcha.md` |
| playbook | `reference/templates/playbook.md` |
| map | `reference/templates/map.md` |
| thinking | `reference/templates/thinking.md` |
| preference | `reference/templates/preference.md` |
| runbook | `reference/templates/runbook.md` |
| tooling | `reference/templates/tooling.md` |
| checkpoint | `reference/templates/checkpoint.md` |
| session-context | `reference/templates/session-context.md` |
| rejection | `reference/templates/rejection.md` |
| session-summary | `reference/templates/session-summary.md` |
| INDEX.md | `reference/templates/index.md` |
| hot.md | `reference/templates/hot.md` |
