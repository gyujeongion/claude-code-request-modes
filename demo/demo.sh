#!/usr/bin/env bash
# Real demo: pipes 3 prompts through the actual UserPromptSubmit hook and shows how the
# router classifies each and turns the irrelevant rule-layers OFF. The context line is the
# hook's real output; the layer line summarizes that context's policy.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$ROOT/skills/request-modes/hooks/request_modes_hook.py"
say(){ printf '\033[1;36m$ %s\033[0m\n' "$1"; sleep .5; }
ctx(){ echo "{\"prompt\":\"$1\"}" | python3 "$HOOK" \
  | python3 -c 'import json,sys;print("  "+json.load(sys.stdin)["hookSpecificOutput"]["additionalContext"].split(chr(10))[0])'; sleep .3; }
lay(){ printf '\033[2m  %b\033[0m\n' "$1"; sleep 1.3; }

echo; printf '\033[1mSame agent, different brain — the router turns the wrong rulebooks OFF.\033[0m\n'; sleep 1.2; echo
say 'claude "throw together some side-project ideas for this weekend"'
ctx "throw together some side-project ideas for this weekend"
lay "L1 style ✓   L4 rigor ✗ OFF   L5 divergence ✓ FULL   → wide-open ideas, no hedging"; echo
say 'claude "run the migration against the prod database"'
ctx "run the migration against the prod database"
lay "L3 safety ✓ FULL   L5 divergence ✗ OFF   → confirm target + rollback first"; echo
say 'claude "review this auth middleware for security holes"'
ctx "review this auth middleware for security holes"
lay "L1 style ✗ OFF   L4 rigor ✓ FULL   → adversarial bug hunt with severity"; echo
printf '\033[1;32mclassify → activate only what applies → OFF the rest. Automatic, every prompt.\033[0m\n'; sleep 2.5
