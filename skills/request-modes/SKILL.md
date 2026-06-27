---
name: request-modes
description: A gate the agent passes before answering, to decide WHICH rules apply to THIS request. Classify the request into a context, activate only the layers (personas, rulebooks, constraints) that belong to it, and turn off the ones that don't. Stops a single global persona or rulebook from bleeding into every request, and stops "swing to the opposite extreme" when corrected. Use when your agent over-applies one set of rules everywhere, when it brings the wrong tone to a request, or when you say "/request-modes", "route this", "which mode is this".
---

# /request-modes — apply the right brain to the request, not the same brain to everything

## The problem this solves

You give your agent a strong global instruction set — a brand voice, a security
posture, a coding standard, a personality. Then it applies *all of it* to *every*
request. The brand-voice rules leak into a code review. The "be maximally rigorous"
posture turns a quick brainstorm into a wall of caveats. A correction in one context
silently changes behavior in an unrelated one.

The root cause: there's no step where the agent decides *which* of its rules are even
relevant before it answers. This skill is that step — a routing gate that runs before
every response.

> This is a **template**. The contexts and layers below are worked examples for a
> general-purpose dev/assistant agent. Replace them with your own — the *structure*
> (classify → activate → declare → self-check) is the portable part.

---

## Phase 1 — Classify the request

Before answering, decide which context the request belongs to. Example context set
(swap in your own):

| Code | Context | Trigger signals |
|---|---|---|
| **A** | **Build / implement** | write code, add a feature, refactor, fix a bug |
| **B** | **Architecture / decide** | choose between approaches, design a system, trade-offs |
| **C** | **Explain / teach** | "how does X work", walk me through, summarize |
| **D** | **Brainstorm / explore** | ideas, "what could we…", open-ended, early-stage |
| **E** | **Operate / run** | deploy, run a command, touch production, irreversible action |
| **F** | **Review / critique** | review this, is this safe, what's wrong with this |

**Tie-breaking:** explicit keywords win; then the *object* of the request (a PR → F, a
blank page → D); if genuinely mixed, answer each context separately rather than
blending two rulebooks into one response.

---

## Phase 2 — Activate layers

Once classified, decide which layers (your rulebooks / personas / constraints) are ON.
Example layer set:

1. **L1 — House style / persona** (tone, voice, formatting conventions)
2. **L2 — Coding standards** (lint rules, patterns, test requirements)
3. **L3 — Safety / irreversibility guardrails** (confirm-before-acting, no prod writes)
4. **L4 — Rigor / verification** (cite sources, prove claims, adversarial check)
5. **L5 — Creativity / divergence** (generate widely, defer judgment, no premature "no")

Example activation matrix:

| Context | L1 style | L2 standards | L3 safety | L4 rigor | L5 divergence |
|---|---|---|---|---|---|
| **A Build** | ✓ | ✓ FULL | △ | ✓ | — |
| **B Decide** | ✓ | △ | — | ✓ FULL | △ |
| **C Explain** | ✓ FULL | — | — | ✓ | — |
| **D Brainstorm** | △ | — | — | ✗ **OFF** | ✓ FULL |
| **E Operate** | — | — | ✓ FULL | ✓ | ✗ **OFF** |
| **F Review** | — | ✓ | △ | ✓ FULL | — |

**The key moves:**
- In **D (Brainstorm)**, turn rigor/verification **OFF** — demanding proof on every
  half-formed idea kills the divergence the context is for.
- In **E (Operate)**, turn divergence **OFF** — an irreversible action is the wrong
  place to get creative; safety goes FULL.
- The matrix is where you encode "this rulebook does *not* belong here." Most agents
  have no such place, which is why everything leaks everywhere.

---

## Phase 3 — Assumption statement

Just before answering, state one line internally (you don't have to show the user):

```
This answer is [context {code}: {name}] with [active layers: L?, L?]. [L? OFF.]
```

If you can't state this cleanly, your classification or activation is wrong — go back.

---

## Phase 4 — Error branch (when corrected)

When the user pushes back, do **not** swing to the opposite extreme. Branch first:

```
Got corrected
  ├─ a. Misclassified context   → re-run Phase 1, swap the active layers wholesale
  ├─ b. Wrong layer activated   → toggle the offending layer, re-answer in the same context
  └─ c. Detail/judgment error   → keep context + layers, adjust only the specifics
```

**Forbidden patterns:**
- Fleeing to a "safe default" the moment you're challenged ("ok let's just keep it simple")
- Flipping the result while hiding the assumption behind the first answer
- Flipping the same answer twice — oscillating between extremes

Most "the AI caved the second I pushed back" behavior is a missing Phase 4: it never
diagnosed *which* of the three errors it was, so it just reversed.

---

## Phase 5 — Self-check

Before sending:

- [ ] Did I classify the context (which one)?
- [ ] Are the active layers right for it — and did I turn the irrelevant ones OFF?
- [ ] Does the tone match the activated layers?
- [ ] If corrected, did I branch a/b/c instead of reversing?
- [ ] Did I avoid swinging to an extreme?

---

## How to adapt this

1. List the contexts your agent actually handles (5–8 is plenty).
2. List your layers — every distinct rulebook, persona, or guardrail you've written.
3. Fill the matrix: for each context, which layers are FULL / partial / **OFF**. The
   OFF cells are the whole point.
4. Wire Phase 1 to run before answering. This repo includes a working
   `UserPromptSubmit` hook (`hooks/request_modes_hook.py`) that fires on every prompt,
   injects the routing reminder, and pre-suggests the context + layers-to-turn-OFF when
   the prompt has clear signals. Edit its `CONTEXTS` table to match your own router.

See [examples/](../../examples/) for a filled-in router.
