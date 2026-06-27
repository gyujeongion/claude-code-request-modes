#!/usr/bin/env python3
"""
Tests for request_modes_hook.detect — run: python3 hooks/test_hook.py
No framework, stdlib only. Exits non-zero on failure.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from request_modes_hook import detect  # noqa: E402

CASES = [
    # (prompt, expected context label prefix or None)
    ("throw together some ideas for a weekend project", "D Brainstorm"),
    ("run the migration against prod", "E Operate"),
    ("review this auth middleware", "F Review"),
    ("zustand vs redux, which should I use?", "B Decide"),
    ("what time is it", None),
    # The shadowing case: low-stakes 'idea' must NOT override a prod action.
    ("I have no idea how to safely run this prod migration", "E Operate"),
    # Review + idea mixed: review (higher risk) wins over brainstorm.
    ("any ideas on how to review this for vulnerabilities?", "F Review"),
]


def main():
    failures = 0
    for prompt, expected in CASES:
        label, _ = detect(prompt)
        got = label.split()[0] + " " + label.split()[1] if label else None
        ok = (got == expected) if expected else (label is None)
        status = "ok " if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"  [{status}] {prompt!r} -> {label} (expected {expected})")
    if failures:
        print(f"\n{failures} test(s) failed")
        sys.exit(1)
    print(f"\nAll {len(CASES)} tests passed")


if __name__ == "__main__":
    main()
