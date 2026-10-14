#!/usr/bin/env python3
"""measure-redundant-reads.py — compute the five Bar-A read metrics from a transcript.

Usage:
    python3 measure-redundant-reads.py transcript.jsonl [baseline.txt]

Transcript: one JSON object per line (see reference/measurement.md, section 2).
    read            {"ts": "...", "agent": "main"|"sub", "path": "...", "chars": N}
                    kind omitted -> treated as a read
    cache_write     {"ts": "...", "kind": "cache_write", "chars": N}
    subagent_prompt {"ts": "...", "kind": "subagent_prompt", "text": "..."}

Baseline file: key=value lines (see reference/measurement.md, section 4), e.g.
    uncached_tokens=23370

Output: greppable key=value lines plus a verdict line.
Exit codes: 0 success; 1 malformed input / unreadable file / unusable baseline; 2 usage.
"""

from collections import Counter
import json
import re
import sys

# P4 pinned sentence — the subagent-coverage match string (verbatim;
# whitespace-normalized on both sides during comparison, backticks required).
PINNED_SENTENCE = (
    "Before reading any shared context files, read "
    "`./docs/brain/session-context.md` if present; use cached summaries "
    "instead of re-reading unchanged files; never write to it \u2014 report "
    "findings to the main agent."
)

RATIO_TARGET = 1.2          # redundant-read ratio target (<= 1.2)
SAVINGS_TARGET = 30.0       # read-token savings % target (>= 30)
COVERAGE_TARGET = 1.0       # subagent coverage target (== 1.0)

# Baseline keys in resolution priority; (key, divisor): byte keys are /4 -> tokens.
BASELINE_KEYS = (
    ("uncached_tokens", 1),
    ("tokens", 1),
    ("md_tokens", 1),
    ("uncached_bytes", 4),
    ("bytes", 4),
    ("md_bytes", 4),
)

USAGE = __doc__


class TranscriptError(Exception):
    """Raised for any input the script cannot process."""


def normalize_ws(text):
    """Collapse all whitespace runs to single spaces (for sentence matching)."""
    return re.sub(r"\s+", " ", text).strip()


def to_nonneg_int(value, line_no, field):
    """Coerce a JSON field to a non-negative int; raise TranscriptError otherwise."""
    if isinstance(value, bool):
        raise TranscriptError(
            "line %d: field '%s' must be a non-negative integer, got bool" % (line_no, field))
    if isinstance(value, int):
        num = value
    elif isinstance(value, float) and value.is_integer():
        num = int(value)
    elif isinstance(value, str) and re.fullmatch(r"\d+", value.strip()):
        num = int(value.strip())
    else:
        raise TranscriptError(
            "line %d: field '%s' must be a non-negative integer, got %r" % (line_no, field, value))
    if num < 0:
        raise TranscriptError(
            "line %d: field '%s' must be >= 0, got %d" % (line_no, field, num))
    return num


def parse_transcript(path):
    """Parse the JSONL transcript into (reads, cache_writes, prompts)."""
    reads = []         # (agent, path, chars)
    cache_writes = []  # chars
    prompts = []       # prompt text
    with open(path, "r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, 1):
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise TranscriptError("line %d: invalid JSON: %s" % (line_no, exc))
            if not isinstance(obj, dict):
                raise TranscriptError(
                    "line %d: expected a JSON object, got %s" % (line_no, type(obj).__name__))
            kind = obj.get("kind", "read")
            if kind == "read":
                if "path" not in obj:
                    raise TranscriptError("line %d: read line missing 'path'" % line_no)
                path_val = obj["path"]
                if not isinstance(path_val, str) or not path_val.strip():
                    raise TranscriptError(
                        "line %d: 'path' must be a non-empty string" % line_no)
                if "chars" not in obj:
                    raise TranscriptError("line %d: read line missing 'chars'" % line_no)
                chars = to_nonneg_int(obj["chars"], line_no, "chars")
                agent = str(obj.get("agent", "main")).strip().lower()
                if agent not in ("main", "sub"):
                    sys.stderr.write(
                        "warning: line %d: unknown agent %r (expected main|sub) - counting as 'other'\n"
                        % (line_no, obj.get("agent")))
                reads.append((agent, path_val.strip(), chars))
            elif kind == "cache_write":
                chars = obj.get("chars")
                if chars is None:
                    chars = obj.get("bytes")
                if chars is None:
                    raise TranscriptError(
                        "line %d: cache_write line missing 'chars'" % line_no)
                cache_writes.append(to_nonneg_int(chars, line_no, "chars"))
            elif kind == "subagent_prompt":
                text = obj.get("text")
                if not isinstance(text, str) or not text.strip():
                    raise TranscriptError(
                        "line %d: subagent_prompt line missing non-empty 'text'" % line_no)
                prompts.append(text)
            else:
                sys.stderr.write(
                    "warning: line %d: skipping unknown kind %r\n" % (line_no, kind))
    return reads, cache_writes, prompts


def parse_baseline(path):
    """Return the uncached token total from a key=value baseline file."""
    found = {}
    with open(path, "r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise TranscriptError(
                    "%s:%d: cannot parse baseline line %r (expected key=value, "
                    "e.g. uncached_tokens=23370)" % (path, line_no, line))
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip()
            m = re.fullmatch(r"([\d,]+)", val)
            if not m:
                raise TranscriptError(
                    "%s:%d: baseline value for '%s' must be a number, got %r"
                    % (path, line_no, key, val))
            num = int(val.replace(",", ""))
            if key in found:
                raise TranscriptError("%s:%d: duplicate key '%s'" % (path, line_no, key))
            found[key] = num
    for key, divisor in BASELINE_KEYS:
        if key in found:
            return found[key] / divisor
    known = ", ".join(k for k, _ in BASELINE_KEYS)
    raise TranscriptError(
        "%s: no recognized baseline key (expected one of: %s)" % (path, known))


def fmt(v):
    return "%.2f" % v


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(USAGE)
        return 0 if len(argv) >= 2 else 2
    if len(argv) > 3:
        print("error: too many arguments", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2

    transcript_path = argv[1]
    baseline_path = argv[2] if len(argv) == 3 else None

    try:
        reads, cache_writes, prompts = parse_transcript(transcript_path)
        baseline_tokens = parse_baseline(baseline_path) if baseline_path else None
        if baseline_tokens is not None and baseline_tokens <= 0:
            raise TranscriptError(
                "%s: uncached token total must be > 0, got %s" % (baseline_path, baseline_tokens))

        total_reads = len(reads)
        unique_files = len({path for _, path, _ in reads})
        reads_by_agent = Counter(agent for agent, _, _ in reads)
        cached_tokens = sum(chars for _, _, chars in reads) / 4.0
        bootstrap_tokens = sum(cache_writes) / 4.0

        pinned_norm = normalize_ws(PINNED_SENTENCE)
        prompts_pinned = sum(1 for text in prompts if pinned_norm in normalize_ws(text))
        prompts_total = len(prompts)
        coverage = (prompts_pinned / prompts_total) if prompts_total else 1.0

        ratio = (total_reads / unique_files) if unique_files else None
        ratio_ok = None if ratio is None else ratio <= RATIO_TARGET

        if baseline_tokens is None:
            saved_tokens = None
            savings_percent = None
        else:
            saved_tokens = baseline_tokens - cached_tokens
            savings_percent = saved_tokens / baseline_tokens * 100.0
        savings_ok = None if savings_percent is None else savings_percent >= SAVINGS_TARGET
        bootstrap_ok = None if saved_tokens is None else bootstrap_tokens < saved_tokens
        coverage_ok = coverage >= COVERAGE_TARGET - 1e-9

        print("# redundant-read metrics: %s" % transcript_path)
        print("total_reads=%d" % total_reads)
        print("unique_files=%d" % unique_files)
        if ratio is None:
            print("redundant_read_ratio=undefined (no reads)")
            print("redundant_read_ratio_ok=undefined")
        else:
            print("redundant_read_ratio=%.2f" % ratio)
            print("redundant_read_ratio_ok=%s" % ("true" if ratio_ok else "false"))
        print("reads_main=%d" % reads_by_agent.get("main", 0))
        print("reads_sub=%d" % reads_by_agent.get("sub", 0))
        print("cached_tokens=%s" % fmt(cached_tokens))
        if baseline_tokens is None:
            print("baseline_tokens=unknown (no baseline file)")
            print("saved_tokens=unknown")
            print("savings_percent=baseline not provided")
            print("savings_ok=unknown")
        else:
            print("baseline_tokens=%s" % fmt(baseline_tokens))
            print("saved_tokens=%s" % fmt(saved_tokens))
            print("savings_percent=%.2f" % savings_percent)
            print("savings_ok=%s" % ("true" if savings_ok else "false"))
        print("bootstrap_tokens=%s" % fmt(bootstrap_tokens))
        if bootstrap_ok is None:
            print("bootstrap_ok=unknown (savings unavailable)")
        else:
            print("bootstrap_ok=%s" % ("true" if bootstrap_ok else "false"))
        print("subagent_prompts=%d" % prompts_total)
        print("subagent_prompts_pinned=%d" % prompts_pinned)
        print("subagent_coverage=%.2f" % coverage)
        if prompts_total == 0:
            print("subagent_coverage_ok=true (vacuous: no subagent prompts in transcript)")
        else:
            print("subagent_coverage_ok=%s" % ("true" if coverage_ok else "false"))

        known = [f for f in (ratio_ok, savings_ok, bootstrap_ok, coverage_ok) if f is not None]
        if known and all(known) and len(known) == 4:
            verdict = "PASS"
        elif any(f is False for f in known):
            verdict = "FAIL"
        else:
            verdict = "INCONCLUSIVE"
        print("# verdict: %s" % verdict)
        return 0
    except TranscriptError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    except OSError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
