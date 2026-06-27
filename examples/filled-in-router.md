# A filled-in router (worked example)

This is the example from the skill, shown end-to-end on three real requests so you can
see the routing actually change the answer. Your own router will have different
contexts and layers — this is the *shape*.

**Layers in this agent:**
- L1 house style · L2 coding standards · L3 safety/irreversibility · L4 rigor/verification · L5 divergence

---

## Request 1 — "Throw together some ideas for a side project this weekend"

- **Classify:** D (Brainstorm)
- **Activate:** L5 divergence FULL, L1 style light. **L4 rigor OFF.**
- **Assumption:** *"This is a Brainstorm; rigor OFF, divergence full."*
- **Result:** a wide spread of ideas, no feasibility caveats, no "but consider the
  risks" on every line. If L4 had stayed on (as it does by default in most agents),
  half the answer would be hedging that kills the brainstorm.

## Request 2 — "Run the migration against prod"

- **Classify:** E (Operate)
- **Activate:** L3 safety FULL, L4 rigor on. **L5 divergence OFF.**
- **Assumption:** *"This is an Operate action; safety full, divergence off."*
- **Result:** confirm the target, check for a backup/rollback, surface the
  irreversible step before doing anything. No "here are five creative ways to migrate"
  — creativity is exactly wrong here, so it's off.

## Request 3 — "Review this auth middleware"

- **Classify:** F (Review)
- **Activate:** L4 rigor FULL, L2 standards on. L1 style off.
- **Assumption:** *"This is a Review; rigor full."*
- **Result:** adversarial read for real bugs with severity, not a polite style pass.

---

## And when the user pushes back

> User: "Why are you being so cautious? I just wanted ideas."

This is an **error branch (a) — misclassification.** Request 1 was routed correctly,
but suppose it had been routed to F (Review) by mistake and came back full of caveats.
The fix is *not* "ok, I'll just say yes to everything" (swinging to the safe extreme).
It's: re-run Phase 1 → this is D (Brainstorm) → swap the active layers wholesale (rigor
OFF, divergence FULL) → re-answer in the correct context.

The branch is what prevents the classic *"the agent caved the second I objected"*
failure: it diagnoses *which* error happened before changing anything.
