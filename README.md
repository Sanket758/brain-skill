# brain — a second-brain memory protocol for AI coding agents

**Your agents forget everything between sessions. This one doesn't.**

`brain` is a plain-Markdown memory layer for agentic coding tools (OpenCode, Claude Code,
or any agent with file tools). It gives every project a persistent vault of *decisions,
findings, and reasoning* that agents read before acting and write back after learning
something — so your agent never re-decides what was already decided, never re-investigates
what was already investigated, and never re-thinks what was already thought.

No database. No server. No vector store. Just Markdown files in an Obsidian-compatible
vault your agent can grep — and *you* can browse in Obsidian while the agent works.

```
your-project/
└── docs/brain -> ~/ObsidianVault/your_project/    # symlink = the whole integration
```

## Why

Every coding agent starts each session amnesia-fresh. Context windows refill, the agent
re-reads the same 5 files, re-asks questions you already answered, and re-litigates decisions
you made last week. Stack-memory products try to fix this with embeddings and APIs; the
actual missing piece is simpler — **an agreement about what to remember and when to read it.**

`brain` is that agreement, written down:

- **Read contract** — at the start of every non-trivial task: read the session-context
  cache (so main agent and subagents don't re-read unchanged files), read `hot.md` (last
  known state), read shared user preferences, then grep `decisions/`, `findings/`,
  `runbooks/`, `thinking/` for keywords from the task. If a prior decision is
  authoritative, follow it — don't re-decide.
- **Write contract** — after every decision, rejected alternative, non-obvious bug fix,
  constraint, gotcha, or benchmark, write a structured note with rationale. 16 note types
  cover the taxonomy (`decision`, `rejection`, `finding`, `bugfix`, `constraint`,
  `performance`, `invariant`, `gotcha`, `playbook`, `map`, `preference`, `thinking`,
  `runbook`, `tooling`, `checkpoint`, `session-context`).
- **Session-context cache** — a per-session read cache so the main agent and its subagents
  don't re-read unchanged files (measured; see below).
- **Sub-agent discipline** — one writer per session; subagents read the cache, never write it.

## Measured impact

### A/B test: same repo, same 3 questions, with vs. without the vault

Two agents, ground truth verified to exist *only* in the vault (grep-verified against the
working tree and git history). The without-memory agent was told the vault was off-limits
and to answer "not found" rather than guess. One run per condition — a demonstration, not
a benchmark; token counts are chars ÷ 4. Full method + caveats: [`docs/ab-test.md`](docs/ab-test.md).

| | WITH brain | WITHOUT brain |
|---|---|---|
| Correct answers | **3 / 3** | **0 / 3** |
| Content read | ≈ 6,650 tokens | ≈ 30,570 tokens (**4.4×**) |
| Tool calls | **10** | **~100** |

The 0/3 is by construction — but *proving* the answers weren't in the repo is the expensive
part: the agent without memory grepped the entire working tree, streamed all 10,045 git
objects, and queried the code index (~100 calls to establish absence). The with-memory agent
recalled all three answers from 6 small notes in 10 calls. Decisions and their rationale
were never in the repo — repo + git are not a memory store for *why*.

### Session-cache benchmark (Bar-A, 2026-08-08)

The session-context cache layer was benchmarked with the bundled
[`brain/tools/measure-redundant-reads.py`](brain/tools/measure-redundant-reads.py)
([method](brain/reference/measurement.md)):

| Criterion | Target | Measured | Verdict |
|---|---|---|---|
| Redundant-read ratio | ≤ 1.2 | 1.12 (vs 2.00 baseline) | PASS |
| Read-token savings | ≥ 30% | **43.19%** | PASS |
| Subagent coverage | 1.00 | 1.00 | PASS |
| Bootstrap cost < savings | bootstrap < saved | 454 tok vs 10,095 tok saved (22×) | PASS |
| Non-breaking | additive-only | PASS |

Reproduce everything from the raw transcripts shipped in
[`brain/tools/fixtures/`](brain/tools/fixtures/README-fixtures.md):

```bash
# the "without cache" control shape → ratio 2.00, FAIL
python3 brain/tools/measure-redundant-reads.py brain/tools/fixtures/sample-transcript.jsonl

# the real benchmark → 43.19% savings, PASS
python3 brain/tools/measure-redundant-reads.py \
  brain/tools/fixtures/bar-after.jsonl brain/tools/fixtures/bar-baseline.txt

# the A/B transcripts → 6,650 vs 30,570 tokens read
python3 brain/tools/measure-redundant-reads.py brain/tools/fixtures/ab-with.jsonl
python3 brain/tools/measure-redundant-reads.py brain/tools/fixtures/ab-without.jsonl
```

## Vault layout

```
~/ObsidianVault/
├── <project_name>/            # one per project, path-derived (Tools_myrepo)
│   ├── decisions/             # architecture choices + rationale + rejected alternatives
│   ├── findings/              # investigations: "tried X, failed because Y"
│   ├── runbooks/              # env setup + reproduction commands
│   ├── checkpoints/           # durable state snapshots for resuming work
│   ├── thinking/              # how the model reasoned through hard problems
│   ├── hot.md                 # rolling state: what changed, what's next
│   └── session-context.md     # ephemeral per-session read cache
├── shared/                    # cross-project: user preferences, tooling facts
└── sessions/                  # cross-project session summaries + INDEX.md
```

Each project's folder is symlinked into the project as `./docs/brain/` — agents always
access it through the symlink, never by guessing vault paths.

## Install

### OpenCode

```bash
git clone https://github.com/Sanket758/brain-skill.git
ln -s "$(pwd)/brain-skill/brain" ~/.config/opencode/skills/brain
cp brain-skill/bin/brain-init ~/.local/bin/ && chmod +x ~/.local/bin/brain-init
```

Add to your project's `AGENTS.md` so the agent picks it up automatically:

```markdown
## Memory
Before non-trivial work, read ./docs/brain/hot.md and grep ./docs/brain/decisions/ for
keywords from the task. Write decisions/findings back per the brain skill.
```

### Any other agent (Claude Code, etc.)

Copy the `brain/` directory into your skills directory (e.g. `~/.claude/skills/brain/`) and add the
pointer line to `CLAUDE.md` / `AGENTS.md`. The protocol only requires read/grep/write
file tools.

### Bootstrap a project

```bash
brain-init /path/to/your/project
# creates ~/ObsidianVault/<project>/ + shared/, sessions/, and
# {decisions,findings,thinking} + hot.md; symlinks it to <project>/docs/brain
# (idempotent, safe to re-run)
```

Open `~/ObsidianVault/` as a vault in the Obsidian GUI to browse what your agents know —
graph view included, since every note carries bidirectional `related:` links.

## What's in the box

```
brain/
├── SKILL.md                    # the protocol: read contract, write contract, delegation rules
├── reference.md                # frontmatter schema, wikilinks, note-type bodies (loaded on demand)
├── reference/measurement.md    # how to measure redundant-read savings (the Bar-A method)
├── reference/templates/        # 19 templates: one per note type + hot.md, index, session-summary
└── tools/
    ├── measure-redundant-reads.py   # stdlib-only metrics script (also uv-run friendly)
    └── fixtures/                # raw transcripts: A/B pair + benchmark + control (+ README)
bin/brain-init                  # one-command project bootstrap
docs/ab-test.md                 # A/B methodology, results, caveats
examples/                       # a sample decision note + hot.md
```

## Design notes

- **Why Markdown, not a database?** Agents already have grep. Notes stay diffable,
  portable, and human-readable; Obsidian gives you the viewer for free.
- **Why a write contract?** Memory that's optional decays. The contract says exactly which
  events must be written (decisions, rejected alternatives, bug root causes, constraints,
  measured performance) and which must not (chatter, trivial edits) — plus a mandatory
  duplicate check so the vault doesn't rot into competing notes.
- **Why per-project isolation?** Cross-project memory leaks are worse than no memory.
  `shared/` is the only cross-project zone, reserved for genuinely global facts.
- **Why symlinks?** The agent accesses memory through a path *inside the project*, so it
  works uniformly regardless of where the vault lives, and `brain-init` can move/rename
  the vault without touching agent instructions.

## License

MIT — see [LICENSE](LICENSE).
