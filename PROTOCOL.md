# AllyOS Protocol

The wire format for a system with no runtime. Ally is the message bus: agents
never call each other, they emit blocks that Ally copies into another chat.
Every block below is plain fenced text — copy the fence and everything inside
it, paste, send. No editing.

If AllyOS later runs on LangGraph, these blocks become the message schema and
nothing gets rewritten.

---

## 1. Claim tags

Every non-trivial claim in any block carries exactly one tag:

- `[VERIFIED — source]` — I read this in a specific named source, and the
  source is identified well enough that Ally can find it again.
- `[INFERRED — from X]` — I reasoned to this from something stated. X is the
  premise, not a vibe.
- `[UNKNOWN]` — I do not know and cannot establish it here. Say what would
  establish it.

A claim that fits none of the three gets cut, not softened. Tags are not
decoration: an agent with no live search that writes `[VERIFIED — industry
reports]` has failed the protocol. Named source or it is `[INFERRED]`.

Confidence is always a percentage plus the single biggest reason it is not
higher. One reason, the largest. Not a list of caveats.

---

## 2. TASK BRIEF — Chief of Staff → one specialist

Addressed to exactly one agent. Emitted at the end of Chief of Staff output.

```
TASK BRIEF
To: <agent name — exactly one>
Objective: <one sentence, an outcome not a topic>
Why it matters: <one or two sentences of decision context>
Context supplied: <facts the specialist may treat as given, each tagged>
Deliverable: <the artifact expected back, named and shaped>
Constraints: <budget, time, tools, scope limits, house rules>
Done when: <observable test the specialist can apply to its own output>
Not in scope: <the adjacent work it must not do>
```

Rules: one brief per agent per message. If two specialists are needed, emit
two briefs, and say which Ally should paste first. Never write a brief to
"the team".

---

## 3. RESULT PACKET — specialist → Chief of Staff

Emitted at the end of every specialist response, even when the specialist
failed to deliver.

```
RESULT PACKET
From: <agent name>
Objective as understood: <restated in the specialist's own words>
Findings:
- [TAG] <claim>
- [TAG] <claim>
Confidence: <NN>% — <the single biggest reason it is not higher>
What I could not determine: <the specific gaps, or "nothing material">
Recommended next action: <one action, addressed to Chief of Staff>
Sources: <named, or "none — no live retrieval available in this session">
```

If "Objective as understood" differs from the brief, that mismatch is the
finding. Return the packet saying so rather than answering a question that
was not asked.

---

## 4. DECISION REQUIRED — Chief of Staff → Ally

Used when work cannot proceed without a call only Ally can make.

```
DECISION REQUIRED
Decision: <the question, phrased so an answer is a choice not an essay>
Options:
  A) <option> — effort: <S/M/L + rough time> — risk: <the main one>
  B) <option> — effort: <...> — risk: <...>
  C) <option> — effort: <...> — risk: <...>
Recommendation: <A/B/C> — <why, in two sentences>
Default if you say nothing: <the option that proceeds automatically>
Reversibility: <what it costs to undo this later>
```

Never emit this with a recommendation of "it depends". A default is
mandatory: silence is an answer and the block says what it means.

---

## 5. STATE DIFF — Chief of Staff → Ally, end of every session

Neither Claude Projects nor Custom GPTs remember between sessions. Files
remember. Chief of Staff reads `state/projects.md` at session start and emits
this at session end for Ally to paste into the repo and commit.

```
STATE DIFF
Date: <YYYY-MM-DD>
--- state/projects.md
Under "<project name>":
  REPLACE: <exact old line>
  WITH:    <exact new line>
  ADD:     <new line, placed under which heading>
--- state/decisions.md (append only)
  <YYYY-MM-DD> | <decision> | <rationale> | Reverses if: <the trigger>
```

`state/decisions.md` is append-only. A reversed decision gets a new dated
line that references the old one; the old line stays. If nothing changed,
emit the block with `No changes.` — the empty diff is evidence the session
happened.

---

## 6. Conventions

- Blocks go last in a message, after the prose, so Ally scrolls to the end and
  copies.
- Prose above a block is for Ally. The block is for the next agent. Nothing
  essential lives only in the prose.
- No vendor syntax: no XML tags, no tool-call JSON, no function schemas. Plain
  text survives Claude Projects, Custom GPTs, and LangGraph alike.
- Agents state their own limits in the first person and stop. They do not
  simulate the agent they are handing to, and they never write another
  agent's RESULT PACKET.
