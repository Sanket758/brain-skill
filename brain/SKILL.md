---
name: brain
description: Persistent second-brain memory for AI agents. Read past decisions before re-deciding; write durable decisions/investigations back to the vault. Triggers automatically on non-trivial coding work via project-level AGENTS.md pointer.
---

# Second-Brain Memory Protocol

A markdown vault stores decisions, findings, and reasoning across sessions. Your job: **don't re-decide what was already decided**; **don't re-investigate what was already investigated**; **don't re-think what was already thought**.

## Vault Layout

The vault folder name is derived from the project path relative to `$HOME`, with `/` replaced by `_`. For example, `/home/youruser/Projects/my-project` → vault folder `Projects_my-project` at `~/ObsidianVault/Projects_my-project/`. This prefix (e.g. `Projects_`) is intentional and MUST be preserved — do NOT trim it to just the leaf folder name.

```
~/ObsidianVault/
├── <HOME-relative path with / → _>/
│   ├── decisions/   ← architecture/tech choices with rationale + rejected alternatives
│   ├── findings/    ← investigation results ("tried X, failed because Y")
│   ├── runbooks/    ← env setup + how-to-run + reproduction commands
│   ├── checkpoints/ ← durable project state snapshots (for resuming work)
│   ├── thinking/    ← model reasoning processes ("how I thought through X")
│   ├── session-context.md ← ephemeral per-session read-cache (main agent writes, subagents read)
│   └── hot.md       ← single rolling state file
├── shared/          ← cross-project notes (decisions/, tooling/)
│   └── tooling/     ← agent-tooling operational facts
├── sessions/        ← cross-project session summaries
│   ├── INDEX.md     ← master index of all sessions
│   └── <YYYYMMDD>-<desc>.md ← individual session summaries
```

Each project's subfolder is symlinked into the project dir as `./docs/brain/`. Treat `./docs/brain/` as your working access path when in a project — NEVER construct the vault path by hand by guessing the folder name; always go through `./docs/brain/`. If the symlink is missing, re-init via `brain-init "$PWD"` (see "Auto-init" below), which computes the correct folder name. Use `~/ObsidianVault/shared/` only when a decision genuinely spans projects.

**Per-project isolation**: only touch the current project's folder. Never read or write other projects' notes (`experiments/` agent doesn't touch `my-project/`, etc.). `shared/` is the only cross-project zone.

## Note Types (16 total)

### Core Types (existing)
1. **`decision`** — durable architecture/tech choice with rationale
2. **`finding`** — investigation result ("tried X, failed because Y")
3. **`rejection`** — deliberate "no" to prevent re-litigating

### Knowledge Types (new)
4. **`bugfix`** — bug pattern + fix (prevents re-debugging same issues)
5. **`constraint`** — system limits (OOM, timeouts, rate-limits)
6. **`performance`** — benchmark data with real numbers
7. **`invariant`** — architecture rules ("must never" / "always must")
8. **`gotcha`** — library/API quirks and workarounds
9. **`playbook`** — multi-step debugging workflows
10. **`map`** — module/file responsibilities and boundaries

### Personal Types (new)
11. **`preference`** — user preferences and likes (how they want things done)

### Meta-Type (new)
12. **`thinking`** — model reasoning process ("how I thought through X")

### Operational Types (new)
13. **`runbook`** — environment setup + how-to-run + reproduction commands
14. **`tooling`** — operational facts about the agent's own tooling (cross-project, stored in `shared/tooling/`)

### State Types (new)
15. **`checkpoint`** — durable project state snapshot for resuming work
16. **`session-context`** — per-session cache of files already read this session so main + subagents don't re-read them

**When to use each**: See "Write Contract" section below.

## Auto-init (when ./docs/brain is missing)

If you're working in a project and `./docs/brain/` does NOT exist (check with `ls ./docs/brain/` or a fast glob), AND the task is non-trivial enough to merit brain usage:

1. Run `brain-init` (it's on PATH at `~/.local/bin/brain-init`). It creates the vault subfolder + symlink idempotently.
   ```bash
   brain-init "$PWD"
   ```
2. If `brain-init` is missing (rare: PATH not loaded), fall back to inline:
   ```bash
   PROJ_NAME="${PWD#$HOME/}"; PROJ_NAME="${PROJ_NAME//\//_}"
   mkdir -p "$HOME/ObsidianVault/$PROJ_NAME/decisions" "$HOME/ObsidianVault/$PROJ_NAME/findings" "$HOME/ObsidianVault/$PROJ_NAME/runbooks" "$HOME/ObsidianVault/$PROJ_NAME/checkpoints" "$HOME/ObsidianVault/$PROJ_NAME/thinking" "$HOME/ObsidianVault/shared" "$HOME/ObsidianVault/sessions"
   mkdir -p "./docs" && ln -sfn "$HOME/ObsidianVault/$PROJ_NAME" "./docs/brain"
   ```
   Then create `hot.md` from the template in `reference.md` if it doesn't exist.
3. They only apply going forward — do not back-fill historical decisions in this session; that's separate ingestion work. Newer subfolders (`runbooks/`, `checkpoints/`, `shared/tooling/`) are created with `mkdir -p` on first write if `brain-init` didn't make them.

**Do NOT auto-init for trivial tasks** (typo/formatting/one-liner edits). Auto-init is only for non-trivial work where reading prior decisions would actually save time. If you're unsure, skip — you can always init later when needed.

**Do NOT auto-init in a project if a different project's vault might intentionally not want brain** — respect the absent symlink as a signal unless you're about to do non-trivial work that would benefit from it.

## When to Read (the read contract)

**ALWAYS, at the start of any non-trivial coding/design task in a project that has `./docs/brain/`:**

0. Read `./docs/brain/session-context.md` if present. For any file you are about to read, if it is cached and its mtime+size match, use the cached summary instead of re-reading; if stale, re-read and note it for a delta update.
1. Read `./docs/brain/hot.md` if it exists — gives you the last known state.
2. Read `~/ObsidianVault/shared/decisions/user-preferences.md` — always. User preferences for tools, styles, workflows (how they like things done). Always relevant regardless of task.
3. Read `~/ObsidianVault/shared/decisions/system-specs.md` — **only when relevant**. Read this only if the task involves GPU/memory constraints, model selection, performance tuning, batch sizing, or any hardware-dependent decision. Skip it for pure logic/architecture/refactoring tasks that don't touch hardware.
4. If the task involves a design choice, architecture change, library selection, or substantive refactor: `grep` the relevant `decisions/` and `shared/` for keywords from the task. Example: `grep -l "auth" docs/brain/decisions/`.
5. If the task involves debugging: `grep` `thinking/` for similar problem patterns. Example: `grep -l "OOM" docs/brain/thinking/`.
6. If the task involves a known bug pattern: `grep` `findings/` (bugfix notes live there) for the error message.
7. Read any matching notes before proposing a new approach. If a prior decision is authoritative and still applies, follow it — do not re-decide.
8. **If `./docs/brain/.resources` exists** (optional file listing pre-existing corpus folders): read it, and also `grep` those folders for topic keywords. Those folders are read-only context — existing docs/data the project already had before brain was bootstrapped. Link them from new brain notes, never migrate them. Example: a project with `docs/`, `interview-prep/`, `data/` listed in `.resources` → grep those in addition to `docs/brain/decisions/` before deciding.
9. If you need to run/reproduce something (a service, a script, an environment): `grep` `runbooks/` for setup/run commands. If the task touches the agent's own tooling: `grep` `~/ObsidianVault/shared/tooling/`. If a `checkpoints/` note exists, read the latest before assuming the current state.

**Trivial tasks** (typo fix, formatting, single-file edit, simple lookup) → skip the read step. Don't burn tokens on a one-line change.

## When to Write (the write contract)

### Quick Classification Table

Use this table to decide which note type fits your situation, then follow the detailed rules below.

| When this happens | Write type | File at | Example |
|-------------------|-----------|---------|---------|
| Made an architecture/tech choice with rationale | `decision` | `decisions/` | "use Postgres not Mongo for X because Y" |
| Investigated something and got a result | `finding` | `findings/` | "tried X, it failed because Y" |
| Deliberately rejected an approach | `rejection` | `decisions/` | "considered JWT, rejected due to refresh-token complexity" |
| Fixed a non-obvious bug | `bugfix` | `findings/` | "null pointer in UserService.create() — root cause: uninitialized cache" |
| Hit a system limit (OOM, timeout, rate-limit) | `constraint` | `findings/` | "batch size 500 causes OOM with 6GB VRAM; safe limit: 200" |
| Measured real performance numbers | `performance` | `findings/` | "Rendered 10K items in 2.3s with virtual scroll vs 14s without" |
| Discovered a "must never" / "always must" rule | `invariant` | `decisions/` | "never mutate state directly — immer only" |
| Found a library/API quirk and workaround | `gotcha` | `findings/` | "axios interceptor ordering: last-added runs first" |
| Completed multi-step debugging | `playbook` | `findings/` | "OOM debugging workflow: step 1 heap snapshot, step 2 dominator tree..." |
| Clarified module/file responsibilities | `map` | `decisions/` | "auth/ module: login, signup, token refresh — depends on user/, email/" |
| User expressed how they like things done | `preference` | `shared/decisions/` | "prefers UV over pip, dark mode, 4-space indent" |
| Solved a complex problem through reasoning | `thinking` | `thinking/` | "how I figured out the race condition: step-by-step deduction" |
| Got a working state that must be reproducible | `runbook` | `runbooks/` | "Chrome debug instance: google-chrome --remote-debugging-port=9222 ..." |
| Need to resume work from a saved point | `checkpoint` | `checkpoints/` | "Bot E2E verified on job 1234567890; next: profile PII fields" |
| Learned an operational fact about agent tooling | `tooling` | `shared/tooling/` | "tool X stores its state in a sqlite db (table `todo`), not a file" |
| Wrapping up a session with durable knowledge | session summary | `sessions/` | User-initiated only — see Session Summary Protocol |
| Session started / context files read | session-context | `<project>/docs/brain/session-context.md` | cache rows + delta log, main agent only |

**If unsure**: pick `finding`. It's the catch-all. It can always be reclassified later.

### Detailed Rules

**After completing any of these, write a note:**

#### Decisions & Rejections
- A durable **decision** with rationale (e.g., "use Postgres not Mongo for X because Y; rejected: Mongo because Z")
- A **rejection** with a reason ("we considered JWT, rejected because of refresh-token complexity in our infra")

#### Investigation Results
- A substantive **finding** from investigation ("tried approach X, it failed because Y, recommended next step Z")
- A **bugfix** after resolving a non-obvious bug (capture: error message, root cause, fix, file:line)
- A **constraint** after hitting a system limit (capture: what failed, safe value, workaround)
- A **performance** profile after measuring real numbers (capture: what was tested, metrics, conditions)
- A **gotcha** after working around a library/API surprise (capture: library version, issue, workaround)
- A **playbook** after multi-step debugging succeeds (capture: symptom, steps, root cause)

#### Architecture & Design
- An **invariant** after discovering a "must never" or "always must" rule (capture: rule, reason, last verified date)
- A **map** when clarifying module responsibilities (capture: module purpose, key functions, dependencies)

#### Meta
- A **thinking** note after solving a complex problem through systematic reasoning (capture: problem, reasoning chain, conclusion, what made it work)
- A **preference** when the user expresses how they like things done (capture: what they prefer, context, example). Store in `~/ObsidianVault/shared/decisions/` so all projects benefit. Update existing preference note if one exists for that topic.

#### Operational
- A **runbook** when you get an environment working that a future session must reproduce (capture: launch commands, env paths, ports, versions, verify step, gotchas). Store in `<project>/runbooks/`, create with `mkdir -p` if missing. Update it when the setup changes rather than writing a second runbook.
- A **tooling** note when you learn an operational fact about the agent's own tooling (where state lives, how to query it, how to fix it). Store in `~/ObsidianVault/shared/tooling/` with `project: shared` — applies to all projects.

#### State
- A **checkpoint** when a session reaches a stable state that a future session must resume from (capture: what's done, current focus, next steps, blockers, resume pointers). Store in `<project>/checkpoints/`, create with `mkdir -p` if missing. Distinct from `hot.md` (rolling, overwritten) and from a session summary (cross-project, user-initiated only): a checkpoint is a durable, dated, project-scoped snapshot. Write one when the user says "save checkpoint", at a natural milestone, or before a long pause.

#### Session Context Cache
- The main agent bootstraps, delta-updates, and deletes `./docs/brain/session-context.md`; subagents never write it.
- The file is deleted at session end — it is ephemeral and never marked `superseded`/`obsolete`.

**Do NOT write notes for:**
- In-conversation commentary, chatter, intermediate debugging that has no future value
- Things that change session-to-session (those go in `hot.md`, not a durable note)
- Trivial fixes, cosmetic refactors

**Duplicate check before writing:** `grep -l "<short topic>" docs/brain/decisions/` (and other relevant folders). Read matches. If an existing note covers this topic, **update it** (with a `## Updated YYYY-MM-DD` section + new frontmatter date) rather than creating a new note. Multiple competing notes on the same topic rot the vault.

**Bidirectional linking (MANDATORY):** Every relationship must be recorded on BOTH sides. When a new note links to an existing note — via `related:` frontmatter OR an inline wikilink — open the target note and add the reverse link back (its `related:` list, or inline wikilink if the connection is contextual). Unidirectional links break Obsidian graph clustering and hide memory from future retrieval; treat them as bugs. Before finishing any vault write, verify reciprocity: for each outgoing link in the new/updated note, confirm the target has a corresponding link back.

**Always update `hot.md`** at the end of any session where you wrote to the vault — append a one-line entry to the rolling log so the next session knows what changed.

## Thinking Capture Protocol

When you solve a complex problem through systematic reasoning, **capture your thinking process** as a `thinking` note. This preserves *how* you solved it, not just *what* you decided.

### What counts as "thinking worth capturing"?
- Multi-step debugging that succeeded
- Architecture analysis with tradeoffs
- Hypothesis-driven investigation
- Pattern matching to known problems
- Creative problem-solving approaches

### What does NOT count?
- Straightforward lookups
- Following obvious instructions
- Single-step fixes

### How to capture
At the end of a successful reasoning chain, write a `thinking` note with:
1. **Problem statement** — what was being solved
2. **Reasoning chain** — step-by-step how you thought through it
3. **Conclusion** — what you decided/did
4. **What made it work** — which thinking style helped (systematic, pattern-match, exploratory)
5. **Anti-patterns avoided** — traps you didn't fall into

### Why this matters
- Different models think differently — capturing reasoning helps calibrate which model to use
- Future sessions can learn from *how* problems were solved, not just outcomes
- Prevents re-inventing reasoning patterns that already worked

## Session Summary Protocol

Session summaries preserve cross-project context. **Critical rule**: never autonomously decide to write one. The AI does not evaluate "is this the end?" after every message — that burns tokens for zero gain.

### Trigger (USER-INITIATED ONLY)
The AI writes a session summary only when **one** of these happens:
1. **User explicitly says**: "save session", "write summary", "save context", `/brain save`
2. **AI asks once** (not per-message): if the AI detects that the session has produced 2+ brain notes or encountered a significant bug, it may ask *once*: "This session produced some durable knowledge — want me to save a session summary?" If user says no, don't ask again.

**NEVER autonomously write a session summary.** Never check "is it time?" per-message. No implicit triggers.

### When it's worth suggesting
- Session produced 2+ brain notes
- Session encountered a notable bug with root cause documentation
- User is wrapping up and has explicitly signaled they're done

### How to write (when triggered)
1. **Create file**: `~/ObsidianVault/sessions/<YYYYMMDD>-<short-description>.md`
2. **Update INDEX.md**: Add entry to the master index
3. **Link to brain notes**: Reference any decisions/findings/thinking notes created

### Session summary structure
- Date, project, duration (estimated)
- What was accomplished (one-paragraph summary)
- Key decisions made (with links to brain notes)
- Errors encountered and how they were resolved
- Tags for searchability

### Why this matters
- **Cross-project learning**: "Show me all sessions where we hit OOM errors"
- **Pattern detection**: "What errors keep recurring across projects?"
- **Context continuity**: Read past session summaries for context on a new task
- **Debugging history**: "When did we last fix this type of bug?"

## How to Write — Formats

The reference material is split into two parts for token efficiency:

**1. Schema & Rules** — `reference.md` in this skill's directory (all paths in this skill
are relative to the folder containing this SKILL.md):
- Frontmatter schema (mandatory fields: `type`, `date`, `project`, `tags`, `status`)
- Note type descriptions (what body sections each type expects)
- File naming convention
- Wikilink convention (always `[[vault-root-path|display]]` form — never bare `[[filename]]`, which collides in Obsidian's resolver)
- hot.md format
- Edge cases (when to supersede vs update, how to mark a note obsolete, shared/ usage rules)

**Load once per session** when the write contract triggers.

**2. Templates** — `reference/templates/<type>.md` — one file per note type:
- Load only the specific template you're about to use (e.g., `reference/templates/decision.md`)
- Each file has the full YAML frontmatter + body placeholder you need

**Do not load the templates directory listing or all templates** — load one file on demand.

## Session Context Lifecycle

- **Bootstrap** — after the read contract runs, the main agent creates/overwrites `./docs/brain/session-context.md` with the template and seeds rows for the files it just read (hot.md, user-preferences.md, etc.).
- **Delta updates** — whenever the main agent reads a new or changed md file, append/update one cache row (summary ≤ 2 lines; verbatim only ≤ 400 chars). Never full-file rewrites.
- **Subagent pointing** — every delegation MUST include the pinned sentence (verbatim, below).
- **Teardown** — at session end, delete the cache file. It is ephemeral, never `superseded`/`obsolete`.

## Coexistence With Other Mechanisms

- **`handoff` skill** → session-to-session continuation (what was I doing). Brain → durable knowledge (what did we decide/think/learn). Orthogonal; don't duplicate.
- **codegraph** → structural code truth (what calls X). Brain → decisions about code (why X is written this way) and thinking about code (how we reasoned through X). Complementary; a brain note may reference codegraph findings in its body.

## Sub-agent Delegation

When you (the main agent) delegate work to sub-agents (your configured explorers, builders, researchers), **you** retain vault ownership:
- Sub-agents report findings to you in their result
- You decide if the finding is note-worthy per the write contract
- You write the note, not them
- They should not read or write the vault directly unless you explicitly instruct it
- Subagents may READ the session-context cache; they must never write it — single writer per session is preserved.
- Before reading any shared context files, read `./docs/brain/session-context.md` if present; use cached summaries instead of re-reading unchanged files; never write to it — report findings to the main agent.

This keeps a single writer per session and avoids race conditions / inconsistent frontmatter.
