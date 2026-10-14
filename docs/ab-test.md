# A/B impact test — with vs. without the brain vault

**Date:** 2026-10-14 · **Design:** two agents, identical questions, same repository.

## Method

Ground truth: three answers that exist **only** in the project's `docs/brain/` vault —
verified beforehand by grep-ing the entire working tree, git object database, and reports
for every distinctive phrase (zero hits outside the vault).

Questions covered: (1) implementation approach + rejected alternatives for three specific
portal integrations, (2) why an LLM backend decision was made + rejected alternatives,
(3) cross-cutting root causes of two failures + which fixes were applied.

Conditions:

- **WITH brain** — follow the read contract: `hot.md` → grep `decisions/`, `findings/` →
  read matching notes.
- **WITHOUT brain** — "fresh agent, no memory; `./docs/brain/` and the vault are strictly
  off limits." Explicitly told to say "not found" rather than guess (fabricated answers
  would be scored against ground truth).

Each agent reported every file read (path + approximate chars returned) and its tool-call
count.

## Results

| Metric | WITH brain | WITHOUT brain |
|---|---|---|
| Correct answers | **3 / 3** | **0 / 3** |
| Content read | 26,600 chars ≈ **6,650 tokens** | 122,280 chars ≈ **30,570 tokens** (4.4×) |
| Tool calls | **10** | **~100** |

### WITH brain — trajectory
1 directory listing + 3 targeted greps → 6 note reads → all three answers HIGH confidence.
Bonus: `hot.md` surfaced that a recorded decision's implementation had later been lost
(never committed) — a discrepancy the decision note alone would have hidden.

### WITHOUT brain — trajectory
Full-tree greps (0 hits) → streamed **all 10,045 git objects** (reachable *and* dangling,
0 hits) → dumped the codegraph index (found stale symbols of a deleted function — no
rationale) → concluded "not in this repository" for two questions and "repo contradicts the
premise" for the third. It recovered *current state* where code still held it; it could
never recover *why* — decisions, rationale, and rejected alternatives were never in the repo.

## Interpretation

Without a memory layer, the knowledge didn't degrade — it was **unrecoverable**, because it
had never been written where the agent could find it. The vault converts "impossible" into
six small reads.

## Caveats

- One trial per condition, three questions — this is an illustrative single run, not a
  population statistic.
- The without-condition was instructed to prefer honest "not found" over guessing, which
  is the honest failure mode (and the expensive one — ~100 tool calls for 0 answers).
- Complementary evidence: the session-context cache layer was separately benchmarked
  against pre-registered targets (43.19% token savings, 5/5 criteria PASS) using the
  bundled `brain/tools/measure-redundant-reads.py`.
