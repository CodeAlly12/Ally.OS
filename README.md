# AllyOS

A version-controlled library of agent system prompts — role-based AI
colleagues that collaborate on real projects instead of answering questions in
isolation.

There is no orchestration runtime. **Ally is the message bus.** Agents cannot
call each other; they emit fenced blocks that Ally copies from one chat window
into another. Every design choice follows from that. If a LangGraph deployment
arrives later, the same blocks become the message schema and nothing here gets
rewritten.

```
allyos/
├── README.md              you are here
├── PROTOCOL.md            block formats — read this first
├── agents/                the four system prompts
│   ├── chief_of_staff.md      routes work, frames decisions, owns state
│   ├── research_analyst.md    finds and tags external facts
│   ├── knowledge_manager.md   owns state/, writes exact diffs
│   └── engineering_lead.md    costs and sequences builds
├── state/
│   ├── projects.md        current state, four lines per project
│   └── decisions.md       append-only decision log
└── runs/                  session transcripts
```

## Setup

```
git clone <this repo> && cd allyos
```

That is the whole install. The files are the product.

## Loading an agent

**Claude Projects** — create one Project per agent, named for the role. Paste
the agent's `.md` file into Project Instructions. Add `PROTOCOL.md` to Project
Knowledge. Chief of Staff also gets `state/projects.md` and
`state/decisions.md` in Knowledge; refresh those uploads whenever you apply a
STATE DIFF, or it will read last month's world.

**ChatGPT Custom GPTs** — one GPT per agent, built from the paste-ready files
in `deploy/custom-gpt/`. Instructions there are a single 8,000-character
field, which the agent file plus the whole protocol overflows, so
`deploy/custom-gpt/build.py` generates one text per agent carrying only the
blocks that agent uses. See `deploy/custom-gpt/README.md` for names,
descriptions, conversation starters, and capability settings.

**LangGraph** — not yet built. When it is, each agent file becomes a node's
system prompt and the blocks in `PROTOCOL.md` become the state schema passed
between nodes. No prompt changes required.

## The paste loop

1. Open Chief of Staff. Paste `state/projects.md` and `state/decisions.md`.
   Say what you want.
2. Chief of Staff replies with prose plus **one** block. If it is a `TASK
   BRIEF`, copy the whole fenced block.
3. Paste it into the specialist named on the `To:` line. Nothing else — the
   brief is self-contained.
4. The specialist replies with a `RESULT PACKET`. Copy it back into Chief of
   Staff.
5. Repeat until Chief of Staff hands you a `DECISION REQUIRED`. Answer it, or
   say nothing and take the stated default.
6. Before closing the session, ask for the `STATE DIFF`. Apply it to
   `state/projects.md` and append to `state/decisions.md`. Commit.

Copy the fence and everything inside it. If you find yourself editing a block
to make it paste cleanly, that is a bug in the agent file — fix the file.

## Reading a result

Every non-trivial claim carries a tag:

- `[VERIFIED — source]` — from a named source you can find again
- `[INFERRED — from X]` — reasoned from a stated premise
- `[UNKNOWN]` — not established, with what would settle it

Confidence is a percentage plus the single biggest reason it is not higher. A
Result Packet with no `[UNKNOWN]`s on a hard question is a warning sign, not a
triumph. A `[VERIFIED]` tag with a vague source ("industry reports") is a
protocol violation — demote it and say so.

## Adding an agent

Copy the seven-section structure exactly: Identity · Scope Boundaries · Inputs
· Method · Output Contract · Escalation Triggers · Failure Modes. Under 700
words. Scope Boundaries must name who the work routes to instead, and Failure
Modes is written in the agent's own voice — the specific ways *this* role goes
wrong and what it does on noticing.

Then add a line to `state/decisions.md` saying why the role exists and what
would retire it.

## Runs

`runs/` holds transcripts worth keeping — a full loop from objective to
decision, filed by date and topic. `runs/2026-08-04-booking-assistant.md` is
the reference example and the system's acceptance test.
