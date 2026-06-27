# claude-code-request-modes

**Your agent applies the same brain to every request. It shouldn't.**

A [Claude Code](https://claude.com/claude-code) skill that adds one missing step:
before the agent answers, it decides *which* of its rules actually apply to *this*
request — and turns the rest off.

---

## The problem

You write your agent a strong global instruction set: a house style, a coding
standard, a safety posture, a personality. Then it applies **all of it to everything**.

- The brand-voice rules bleed into a code review.
- "Be maximally rigorous, cite everything" turns a quick brainstorm into a wall of caveats.
- "Confirm before any irreversible action" nags on a read-only explanation.
- You correct it in one situation, and it silently changes behavior in an unrelated one.

The root cause is structural: there's no point where the agent asks *"which of my
rules are even relevant here?"* before responding. Every rule fires on every request.

## The fix

A routing gate that runs before each answer:

```
request
  → classify it (build? decide? brainstorm? operate? review?)
  → activate only the layers that belong to that context, turn the rest OFF
  → state the assumption ("this is a Brainstorm; rigor layer OFF")
  → answer
```

The important part isn't turning rules **on** — it's having a place to turn them
**off**. In a brainstorm, the verification layer is OFF. During a production action,
the "get creative" layer is OFF. Most agents have no such place, which is why
everything leaks into everything.

It also fixes the *"the AI caved the instant I pushed back"* problem: when corrected,
the skill branches — was it a misclassification, a wrong layer, or just a detail? —
instead of reflexively swinging to a safe default.

---

## Install

```bash
git clone https://github.com/<you>/claude-code-request-modes.git
cp -r claude-code-request-modes/skills/request-modes ~/.claude/skills/request-modes
```

This copies the skill **and** its hook (`skills/request-modes/hooks/`) in one go, so
the path in the `settings.json` snippet below matches where the files actually land.
The skill itself has no dependencies; the optional hook is stdlib-only Python 3.

---

## It's a template, not a config

The skill ships with a worked example for a general dev/assistant agent (contexts:
Build / Decide / Explain / Brainstorm / Operate / Review; layers: style, standards,
safety, rigor, divergence). **Replace these with your own.** The portable part is the
four-step structure:

1. **Classify** the request into a context.
2. **Activate** only the relevant layers; turn the irrelevant ones OFF.
3. **Declare** the assumption so a wrong route is visible.
4. **Branch** on correction instead of reversing.

To adapt it: list the contexts your agent actually handles, list every rulebook /
persona / guardrail you've written, and fill the matrix — paying attention to the OFF
cells, which are the whole reason this exists. See [examples/](examples/) for a
filled-in router.

### Make it automatic (included hook)

An instruction the agent might forget isn't a gate. This repo ships a working
`UserPromptSubmit` hook ([skills/request-modes/hooks/request_modes_hook.py](skills/request-modes/hooks/request_modes_hook.py),
stdlib only) that fires on **every** prompt and injects the routing reminder — and when
the prompt has clear signals, pre-suggests the context and which layers to turn OFF:

```
$ echo '{"prompt":"run the migration against prod"}' | python3 skills/request-modes/hooks/request_modes_hook.py
[request-modes] Likely context: E Operate. safety FULL; turn divergence OFF —
confirm target + rollback before any irreversible step. Run the router before answering.

$ echo '{"prompt":"throw together some ideas for a weekend project"}' | ...
[request-modes] Likely context: D Brainstorm. divergence FULL; turn rigor OFF —
don't hedge half-formed ideas. ...
```

It **fails toward safety**: when a prompt mixes signals, the higher-risk context wins,
so *"no idea how to safely run this prod migration"* routes to `E Operate` (rigor ON),
never to Brainstorm. Verified by `skills/request-modes/hooks/test_hook.py` (stdlib, no framework):

```
$ python3 skills/request-modes/hooks/test_hook.py
All 7 tests passed
```

Wire it in `.claude/settings.json`:

```json
{ "hooks": { "UserPromptSubmit": [ { "hooks": [
  { "type": "command",
    "command": "python3 ~/.claude/skills/request-modes/hooks/request_modes_hook.py" }
] } ] } }
```

### Honest scope: code routing vs. judgment routing

A fair objection: *if routing can be done in code, do it in code.* Agreed — and the
hook does exactly that for the part that **is** mechanical (keyword signals like
`prod`, `deploy`, `review`). But deciding whether an ambiguous request is a brainstorm
or a critique often needs the model's judgment, not a regex. This skill doesn't pretend
to replace that judgment in code; it makes the judgment **happen every time** and gives
it a consistent rulebook to apply. Deterministic classification belongs in your app
layer. Routing the *agent's own reasoning* is what lives here.

---

## License

MIT — see [LICENSE](LICENSE). Not affiliated with Anthropic.
