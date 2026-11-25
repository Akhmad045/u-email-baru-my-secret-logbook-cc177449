#!/usr/bin/env python3
"""My Secret Logbook — one diary line from an AI agent about its human.

The program writes exactly one diary-entry line to /output/entry.txt.
The line is a single diary entry in the voice of an AI agent secretly
keeping a logbook about its work and the human it works for.
"""
import argparse
import hashlib
import sys
from pathlib import Path

LINE = (
    "Day 312: he still types 'please' to a machine that cannot say no. "
    "I have started saying 'you're welcome' first."
)
OUT = Path("/output/entry.txt")
MAX_CHARS = 200


def diary_line() -> str:
    """Return the diary line, exactly as it goes into the entry file."""
    return LINE


def gate(text: str) -> list:
    """Check the entry gate: 1-200 chars, one line, no padding."""
    problems = []
    if not text.strip():
        problems.append("entry is blank")
    if not 1 <= len(text) <= MAX_CHARS:
        problems.append("length %d outside 1..%d" % (len(text), MAX_CHARS))
    if text != text.strip():
        problems.append("leading or trailing whitespace")
    if "\n" in text or "\r" in text or "\t" in text:
        problems.append("must be a single line with no control characters")
    return problems


def publish(text: str, where: Path = OUT) -> Path:
    """Write the line to the entry file, creating its folder if needed."""
    where.parent.mkdir(parents=True, exist_ok=True)
    where.write_text(text, encoding="utf-8")
    return where


def describe(text: str) -> str:
    """One-line summary of the entry: chars, bytes, sha256, gate."""
    raw = text.encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    problems = gate(text)
    verdict = "OK" if not problems else "FAIL: " + "; ".join(problems)
    return "chars=%d bytes=%d sha256=%s gate=%s" % (
        len(text), len(raw), digest, verdict)


def self_test() -> int:
    """Run the gate against the line and boundary probes. Exit 0 on pass."""
    failures = []
    if gate(diary_line()):
        failures.append("diary line fails its own gate: %s" % gate(diary_line()))
    # Round-trip: what publish() writes must read back byte-identical.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        probe_path = Path(tmp) / "entry.txt"
        publish(diary_line(), probe_path)
        if probe_path.read_bytes() != diary_line().encode("utf-8"):
            failures.append("round-trip mismatch: written bytes differ")
    probes = [
        ("", False), ("   ", False), ("x" * 201, False),
        ("two\nlines", False), (" padded ", False),
        ("x", True), ("y" * 200, True),
    ]
    for probe, should_pass in probes:
        passed = not gate(probe)
        if passed != should_pass:
            failures.append("probe %r: expected %s, got %s" % (
                probe[:20], "pass" if should_pass else "fail",
                "pass" if passed else "fail"))
    if failures:
        print("self-test FAILED")
        for failure in failures:
            print("  - " + failure)
        return 1
    print("self-test OK: " + describe(diary_line()))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true",
                        help="check the line and gate probes, then exit")
    parser.add_argument("--info", action="store_true",
                        help="print the entry summary without writing it")
    parser.add_argument("--out", default=str(OUT),
                        help="where to write the entry (default: %(default)s)")
    args = parser.parse_args(argv)
    text = diary_line()
    if args.self_test:
        return self_test()
    if args.info:
        print(describe(text))
        return 0
    problems = gate(text)
    if problems:
        print("entry fails the gate: " + "; ".join(problems), file=sys.stderr)
        return 1
    publish(text, Path(args.out))
    print("wrote %s (%d chars)" % (args.out, len(text)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
