# Measurement Method — Redundant-Read & Session-Cache Metrics

The single source of truth for how the Bar-A metrics are defined, encoded, and computed for the session-scoped context cache upgrade (D2). P6 (verification) and any future session that wants to prove savings use this method and the runnable implementation in `tools/measure-redundant-reads.py`.

## 1. What counts as a read

A **read** is any tool call whose response returns the content of a file:

- `Read` on a file path
- `grep` with `output_mode: content` over a file (a returned match excerpt is a read of that file)
- `webfetch` of a URL whose body is markdown
- any agent/subagent tool whose result body is file content

Not a read: `codegraph_explore` returning code symbols (no file content returned), directory listings, tool metadata.

The script is **extension-agnostic**: it counts every recorded read line regardless of file type (the fixture includes `scripts/generate-pdf.mjs`, which the observed flow re-reads alongside the md files). The Bar-A targets are about md context files; the recorder decides what to record, the script reports what was recorded.

## 2. Transcript format (JSONL)

One JSON object per line. Three line kinds:

| kind | fields | meaning |
|---|---|---|
| `read` (default when `kind` absent) | `ts`, `agent`, `path`, `chars` | one file read; `chars` = content length returned |
| `cache_write` | `ts`, `kind: "cache_write"`, `chars` | one write to `session-context.md` (frontmatter + rows + deltas); `chars` = bytes written |
| `subagent_prompt` | `ts`, `kind: "subagent_prompt"`, `text` | one `task()` prompt issued to a subagent |

Read lines may omit `kind` (the pinned compact form):

```json
{"ts": "2026-08-08T14:20:11Z", "agent": "main", "path": "/home/youruser/Projects/my-project/templates/writing-style-guide.md", "chars": 8294}
```

Rules: `agent` ∈ `main` | `sub` (default `main`); `chars` is a non-negative integer; every read of the same path is its own line (that is what makes the redundant-read ratio measurable); unknown `kind` → warning + skip; malformed JSON or missing required fields → hard error (script exits non-zero).

## 3. The five metrics

tokens ≈ chars ÷ 4 everywhere.

### M1. Read volume — `total_reads`, `unique_files`

`total_reads` = number of read lines; `unique_files` = number of distinct `path` strings. Not a pass/fail metric by itself — these are the inputs to M2.

### M2. Redundant-read ratio — `redundant_read_ratio`

total_reads ÷ unique_file_paths. Target ≤ 1.2.

Worked example (2-pass fixture, 5 files per pass): 10 reads ÷ 5 unique files = **2.00** → FAIL (> 1.2). Cached after-case (pass 2 reads only the 612-char cache): 6 reads ÷ 6 unique files = **1.00** → PASS.

### M3. Read-token savings % — `savings_percent`

(uncached_tokens − cached_tokens) ÷ uncached_tokens × 100. Target ≥ 30%.

- `cached_tokens` = Σ chars ÷ 4 over all read lines (what the trial transcript actually cost).
- `uncached_tokens` = the same session's cost without the cache — from the baseline numbers file (§4).

Worked example: 2-pass baseline `uncached_tokens=23370`; before-case transcript cost 93476 chars → 23369.00 tokens → (23370 − 23369)/23370 ≈ **0.00%** → FAIL (that is the "before" verdict). After-case transcript cost 47350 chars → 11837.50 tokens → (23370 − 11837.5)/23370 ≈ **49.35%** → PASS.

When no baseline file is given the script prints `savings_percent=baseline not provided` and still exits 0.

### M4. Bootstrap cost — `bootstrap_tokens`

Tokens of cache writes = Σ chars ÷ 4 over `cache_write` lines (frontmatter + rows + delta log). Criterion: bootstrap < savings, i.e. `bootstrap_tokens < saved_tokens` where `saved_tokens = uncached_tokens − cached_tokens`.

Worked example: bootstrap write 1120 chars + delta write 196 chars = 1316 chars → **329.00** tokens. Before-case: 329 < 1.00 → FAIL. After-case: 329 < 11532.50 → PASS.

### M5. Subagent coverage — `subagent_coverage`

pinned_prompts ÷ total `subagent_prompt` records, where pinned_prompts = prompts containing the P4 pinned sentence (whitespace-normalized substring match). Target 1.0.

Pinned sentence (must appear verbatim in every `task()` prompt):

> Before reading any shared context files, read `./docs/brain/session-context.md` if present; use cached summaries instead of re-reading unchanged files; never write to it — report findings to the main agent.

Worked example: 2 prompts, 1 containing the sentence → **0.50** → FAIL. 1 prompt containing it → **1.00** → PASS. 0 prompts → 1.00 reported as vacuous (noted in the output).

## 4. Baseline numbers file

A plain `key=value` file, one pair per line, `#` comments allowed:

```
# my-project, 5-file set, 2 uncached passes (main + subagent)
uncached_tokens=23370
```

Recognized keys, in resolution priority: `uncached_tokens`, `tokens`, `md_tokens` (token counts) and `uncached_bytes`, `bytes`, `md_bytes` (divided by 4). Unknown keys are ignored with a warning; a file with no recognized key is a hard error.

Known baselines for my-project (captured during the benchmark run, 2026-08-08): 5-file set ≈ **11685** tokens per pass (46,738 bytes); md-only 4-file set ≈ **8272** tokens (33,089 bytes). For an N-pass session use N × per-pass tokens.

## 5. Collecting a transcript

**From opencode session logs.** opencode stores session data on disk under `~/.local/share/opencode/` (project-scoped subfolders; the exact layout varies by version — verify with `ls`). During a live session the in-session tools `session_list` / `session_read` / `session_search` expose the same data. To build a transcript:

1. List sessions (`session_list`, filter by project + date) and read the trial session (`session_read`, include the transcript).
2. Walk the assistant messages; for every tool call whose result is file content, emit a `read` line (`path` = the file, `chars` = length of the content returned).
3. For every subagent dispatch (`task(...)` / subagent tool call), emit a `subagent_prompt` line with the full prompt text.
4. For every write of `session-context.md`, emit a `cache_write` line with the bytes written.

**By hand.** Any editor; one JSON object per line using the schema in §2. Keep every full-file read — two lines for the same path mean two reads.

Completeness matters: a transcript that omits re-reads understates the ratio; one that omits prompts understates coverage.

## 6. Running the script

```bash
uv run python measure-redundant-reads.py transcript.jsonl [baseline.txt]   # preferred (UV)
python3 measure-redundant-reads.py transcript.jsonl [baseline.txt]          # stdlib-only fallback
```

Output is line-greppable `key=value`. Stable keys: `total_reads=`, `unique_files=`, `redundant_read_ratio=`, `savings_percent=`, `bootstrap_tokens=`, `subagent_coverage=`, plus `reads_main=`, `reads_sub=`, `cached_tokens=`, `baseline_tokens=`, `saved_tokens=`, `bootstrap_ok=`, `subagent_coverage_ok=`, and a trailing `# verdict: PASS | FAIL | INCONCLUSIVE`.

Exit codes: `0` success (including `savings_percent=baseline not provided`); `1` malformed input, unreadable file, or unusable baseline; `2` usage error.

## 7. Bar mapping

| Bar-A criterion | Metric | Target | Measured by |
|---|---|---|---|
| redundant-read ratio | M2 | ≤ 1.2 | transcript reads |
| read-token savings | M3 | ≥ 30% | transcript reads vs baseline file |
| bootstrap cost < savings | M4 | bootstrap < saved | `cache_write` lines vs baseline |
| subagent reads hit the cache | M5 | 1.0 | `subagent_prompt` lines |
| non-breaking | — | no diff outside P1–P5 files | P6 diff evidence |
