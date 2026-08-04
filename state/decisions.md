# Decisions

Append-only. Never edit or delete a line. A reversal is a new dated line that
names the one it reverses.

Format: `YYYY-MM-DD | Decision | Rationale | Reverses if: <trigger>`

A line with no reversal trigger is a preference, not a decision, and does not
belong here.

---

2026-08-04 | Ally is the message bus; agents never call each other | There is
no orchestration runtime today, and designing for one that does not exist
produces prompts that fail on the tools actually in use | Reverses if: a
LangGraph deployment runs at least two agents end to end without a human in
the loop

2026-08-04 | Handoffs are fenced plain-text blocks (TASK BRIEF, RESULT PACKET,
DECISION REQUIRED, STATE DIFF) defined in `PROTOCOL.md` | Plain text is
copy-pasteable by hand today and becomes the message schema unchanged if
LangGraph arrives, so nothing gets rewritten | Reverses if: a target platform
cannot round-trip fenced blocks without mangling them

2026-08-04 | Claims are tagged `[VERIFIED — source]` / `[INFERRED — from X]` /
`[UNKNOWN]` rather than banned by a "never speculate" rule | An unenforceable
ban produces hedging and invented sources; a labelling requirement produces
something Ally can audit | Reverses if: agents are observed tagging
consistently but wrongly, at which point the tag itself is the problem, not
the ban

2026-08-04 | State lives in `state/*.md`, re-pasted at session start, never in
model memory | Neither Claude Projects nor Custom GPTs persist context between
sessions | Reverses if: a deployment target gains reliable durable memory that
survives session boundaries

2026-08-04 | `state/decisions.md` is append-only | The audit trail is the point
— a tidied log cannot answer "why did we choose this, and what would change
our minds" | Reverses if: never, while this file exists as a record

2026-08-04 | 700-word ceiling per agent file | Longer prompts do not produce
better agents, they produce agents that ignore the middle | Reverses if: an
agent fails on a real task for want of instruction that cannot be compressed
into the budget

2026-08-04 | v1 of the villa booking assistant is WhatsApp assisted replies —
agent drafts, Ally sends | Captures most of the time saving with no platform
permissions gate; full auto-reply is blocked on an [UNKNOWN] and would be
buying a maybe | Reverses if: the enquiry count comes in above ~20/week, or
Booking.com messaging access is confirmed available to a property this size

2026-08-04 | Chief of Staff's 400-word budget counts prose only, not block
text | The protocol's own required blocks total ~477 words on a full session,
so a budget covering them would forbid briefing, deciding, and saving state in
one sitting | Reverses if: block formats shrink enough that a full session
fits under 400 words in total

2026-08-04 | The orchestration runtime is a plain Python loop over the Messages
API, not LangGraph | The protocol blocks already are the message schema, so the
routing logic is a parser and a dict — LangGraph would add a dependency and a
graph DSL without removing any of that work | Reverses if: the loop needs
durable checkpointing, human-in-the-loop resume, or fan-out across more than a
handful of agents

2026-08-04 | Each agent holds its own message history in the runtime, rather
than sharing one transcript | A specialist that has seen Chief of Staff's
framing tags things [INFERRED] that it should call [UNKNOWN], in good faith,
which destroys the one discipline the system rests on | Reverses if: agents are
observed failing for want of context that a self-contained TASK BRIEF genuinely
cannot carry
