# Fixtures — raw transcripts behind every published number

| File | What it is | Reproduce |
|---|---|---|
| `bar-after.jsonl` + `bar-baseline.txt` | Session-cache benchmark (Bar-A, 2026-08-08): 9 reads / 8 unique, 43.19% savings, bootstrap 454.50 tok, coverage 1.00 → **PASS** | `python3 ../measure-redundant-reads.py bar-after.jsonl bar-baseline.txt` |
| `sample-transcript.jsonl` | The "without cache" control shape: 10 reads / 5 unique → ratio 2.00 → **FAIL** | `python3 ../measure-redundant-reads.py sample-transcript.jsonl` |
| `ab-with.jsonl` | A/B test, WITH-brain agent: 9 content reads (6 notes + 3 grep excerpts), 26,600 chars ≈ 6,650 tok | `python3 ../measure-redundant-reads.py ab-with.jsonl` → `cached_tokens=6650.00` |
| `ab-without.jsonl` | A/B test, WITHOUT-brain agent: 52 content reads, 122,280 chars ≈ 30,570 tok | `python3 ../measure-redundant-reads.py ab-without.jsonl` → `cached_tokens=30570.00` |

Notes:
- A/B transcripts are reconstructed from each agent's own mandatory measurement report
  (every file read + chars returned, self-reported); paths anonymized (`my-project`,
  `youruser`). Tool-call counts (10 vs ~100) are in `docs/ab-test.md`, not derivable
  from these files.
- Token estimates = chars ÷ 4 (same heuristic throughout).
- `bar-after.jsonl` is the verbatim after-case transcript from the Bar-A verification
  report, path-anonymized.
