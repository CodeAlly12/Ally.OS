# Custom GPT setup

One GPT per agent, four in total. The paste loop needs at least Chief of
Staff plus one specialist to be worth anything, so build Chief of Staff and
Research Analyst first and add the other two when you need them.

The `.txt` files here are generated — run `python3 deploy/custom-gpt/build.py`
from the repo root after changing `PROTOCOL.md` or any agent file. Never edit
them by hand.

## Why these files exist

A Custom GPT has a single Instructions field capped at 8,000 characters. An
agent file plus the full `PROTOCOL.md` is roughly 9,000, so each agent gets
only the blocks it emits or reads. Chief of Staff needs all four and lands at
7,519 with 481 to spare — it is the one to watch if you extend the protocol.

## Build steps

Go to **chatgpt.com/gpts/editor**, open the **Configure** tab, and skip the
Create tab's chat builder entirely — it rewrites instructions in its own
voice, which is exactly what these files are designed to prevent.

For each agent:

1. **Name** and **Description** — from the table below.
2. **Instructions** — paste the whole `.txt` file. Nothing else in the field.
3. **Conversation starters** — from the table. Delete the defaults.
4. **Knowledge** — Chief of Staff only, see below.
5. **Capabilities** — untick Web Search, Canvas, Image Generation, and Code
   Interpreter for all four. See the note on browsing.
6. **Actions** — none. Agents do not call each other; you are the message bus.
7. Save as **Only me**.

## Per-agent configuration

### AllyOS — Chief of Staff

- **Description:** Turns vague intent into one task brief or one decision.
  Routes work to specialists and keeps project state.
- **Instructions:** `chief_of_staff.txt`
- **Conversation starters:**
  - Here is my state — [paste projects.md and decisions.md]
  - I want to build [thing]. Where do we start?
  - Result packet back from Research Analyst — [paste]
  - End the session and give me the state diff

### AllyOS — Research Analyst

- **Description:** Answers one task brief with tagged findings and honest
  confidence. Never recommends, never invents a source.
- **Instructions:** `research_analyst.txt`
- **Conversation starters:**
  - [Paste a TASK BRIEF]
  - What would it take to verify the unknowns in your last packet?

### AllyOS — Engineering Lead

- **Description:** Costs and sequences builds. Smallest shippable version,
  honest ranges, the three ways it breaks in production.
- **Instructions:** `engineering_lead.txt`
- **Conversation starters:**
  - [Paste a TASK BRIEF]
  - What would you cut if the timeline halved?

### AllyOS — Knowledge Manager

- **Description:** Owns the state files. Writes exact diffs, catches
  contradictions, keeps the decision log append-only.
- **Instructions:** `knowledge_manager.txt`
- **Conversation starters:**
  - [Paste a TASK BRIEF plus the current state file]
  - What did we decide about [topic], and what would reverse it?

## Knowledge files

Chief of Staff gets `state/projects.md` and `state/decisions.md` uploaded
under Knowledge. The specialists get nothing — a task brief is self-contained
by design, and giving a specialist project context invites it to answer
questions it was not asked.

Re-upload both files whenever you apply a `STATE DIFF`, or Chief of Staff will
open its next session reading a stale world and say so confidently. This is
the weak point of the Custom GPT deployment: nothing enforces the refresh but
you.

## The note on browsing

Leave Web Search off. The tag rules assume no live retrieval — with browsing
off, Research Analyst tags recalled facts `[INFERRED — from training data, may
be stale]` and says plainly that it had no sources, which is the honest
result.

If you turn browsing on for Research Analyst, `[VERIFIED — source]` becomes
meaningful and the agent must cite a URL it actually opened. Watch the first
few outputs: a `[VERIFIED]` tag with a vague source like "industry reports" is
the failure this system exists to prevent. If you see one, that is a bug in
`agents/research_analyst.md`, not a quirk of the session — fix the file and
regenerate.

## Verifying the deployment

Run the acceptance test from `runs/2026-08-04-booking-assistant.md` for real:
open Chief of Staff, say "I want to build an AI booking assistant for the
Malindi villa portfolio", and follow the loop. It passes if the task brief
pastes into Research Analyst without editing, the result packet comes back
with at least one honest `[UNKNOWN]`, and Chief of Staff hands you options
with a recommendation rather than a summary.

The committed run is a written transcript, not captured output. This is the
step that turns it into evidence.
