#!/usr/bin/env python3
"""
request_modes_hook.py — a UserPromptSubmit hook that enforces the context router.

What it does (and doesn't do):
- It does NOT try to fully classify the request in code. Deciding whether a request is
  a "brainstorm" or a "review" often needs the model's judgment, not a regex.
- It DOES guarantee the routing gate is never silently skipped. On every prompt it
  injects a short reminder telling the agent to run the router before answering, and —
  when the prompt contains clear signals — it pre-suggests the likely context and which
  layers to turn OFF. The model still makes the final call; the hook makes sure the
  step happens at all.

This is the deterministic half of the method: the model classifies, the hook ensures
it classifies. Pure code routing belongs in your application layer; routing the
*agent's own judgment* belongs here.

Wire it up in .claude/settings.json:

    {
      "hooks": {
        "UserPromptSubmit": [
          {
            "hooks": [
              { "type": "command",
                "command": "python3 ~/.claude/skills/request-modes/hooks/request_modes_hook.py" }
            ]
          }
        ]
      }
    }

Edit CONTEXTS below to match your own router (same contexts/layers as your SKILL.md).
No dependencies — standard library only.
"""

import sys
import json
import re

# (risk, context label, [keyword regexes], "layers to bias OFF for this context")
# `risk` orders precedence when a prompt matches more than one context. We fail toward
# SAFETY: an irreversible-action signal (Operate) must win over a low-stakes one
# (Brainstorm), so "no idea how to safely run this prod migration" routes to Operate —
# never to "turn rigor off." Higher risk = higher precedence.
CONTEXTS = [
    (4, "E Operate",    [r"\bdeploy", r"\bprod\b", r"production", r"\bmigrat", r"\brm\b",
                         r"drop table", r"force push", r"\bdelete\b", r"\brevert\b"],
     "safety FULL; turn divergence OFF — confirm target + rollback before any irreversible step"),
    (3, "F Review",     [r"\breview\b", r"is this safe", r"what's wrong", r"audit", r"vulnerab"],
     "rigor FULL — adversarial read for real bugs with severity, not a style pass"),
    (2, "B Decide",     [r"\bvs\b", r"should i", r"trade-?off", r"which (one|approach|library)",
                         r"\bdecide\b"],
     "rigor FULL; weigh options explicitly, don't just pick the popular one"),
    (1, "D Brainstorm", [r"\bidea", r"brainstorm", r"what could", r"explore", r"\bdraft\b"],
     "divergence FULL; turn rigor/verification OFF — don't hedge half-formed ideas"),
]

GENERIC = ("No strong signal — classify the request into one of your contexts, activate "
           "only the relevant layers, and turn the irrelevant ones OFF before answering.")


def detect(prompt: str):
    """Return the highest-risk matching context, so low-stakes keywords can never
    shadow a high-risk one (e.g. 'idea' must not override 'prod migration')."""
    p = prompt.lower()
    best = None  # (risk, label, guidance)
    for risk, label, patterns, guidance in CONTEXTS:
        if any(re.search(pat, p) for pat in patterns):
            if best is None or risk > best[0]:
                best = (risk, label, guidance)
    if best is None:
        return None, None
    return best[1], best[2]


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # never block the prompt on a hook error

    prompt = data.get("prompt", "") or ""
    label, guidance = detect(prompt)

    if label:
        msg = (f"[request-modes] Likely context: **{label}**. {guidance}\n"
               f"Run the router (classify → activate layers → state the assumption) "
               f"before answering. The model decides; this is a reminder, not a verdict.")
    else:
        msg = f"[request-modes] {GENERIC}"

    # Claude Code injects this string as additional context for the turn.
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": msg,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
