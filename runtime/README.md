# The runtime

`allyos.py` replaces Ally as the message bus. It loads the same agent files a
Claude Project or Custom GPT would, calls the Claude API, parses the fenced
blocks from `PROTOCOL.md`, and routes them between agents automatically.

Nothing in `agents/` or `PROTOCOL.md` was rewritten to make this work. That was
the point of designing the blocks as plain text.

## Setup

```
pip install -r runtime/requirements.txt
export ANTHROPIC_API_KEY=...        # or: ant auth login
```

## Run

```
python3 runtime/allyos.py "I want to build an AI booking assistant for the Malindi villas"
python3 runtime/allyos.py --search "..."          # Research Analyst gets the web
python3 runtime/allyos.py --effort medium "..."   # cheaper, faster
python3 runtime/allyos.py --no-state "..."        # start Chief of Staff blind
```

It prints each turn as it happens and writes the whole session to `runs/`.

## What it does

1. Loads `state/projects.md` and `state/decisions.md`, hands them to Chief of
   Staff with your objective.
2. On a `TASK BRIEF`, reads the `To:` line and routes the block to that agent —
   the block only, nothing else.
3. On a `RESULT PACKET`, routes it back to Chief of Staff.
4. Stops on `DECISION REQUIRED` or `STATE DIFF`, because both need you.

**Each agent keeps its own message history.** That isolation is deliberate and
load-bearing: a specialist that has seen Chief of Staff's framing will tag
things `[INFERRED]` that it should be calling `[UNKNOWN]`, in good faith. The
runtime enforces the same wall that separate Projects or Custom GPTs give you.

## Tag auditing

Every `RESULT PACKET` is scanned before it goes back to Chief of Staff, and
findings print inline and land in the run file:

- `[VERIFIED — …]` when live retrieval was off — the tag cannot be honest.
- `[VERIFIED — industry reports]` and similar — a source nobody can find again.
- No `[UNKNOWN]` anywhere on a hard question — a warning sign about the agent,
  not a triumph.

The audit reports; it does not silently rewrite the packet. If it fires
repeatedly, the fix is in `agents/research_analyst.md`, not here.

## Tools

`--search` gives Research Analyst `web_search`. It runs server-side, so there
is no execution loop to write — and it changes what the agent is *allowed* to
claim: with the web on, `[VERIFIED]` means a page it actually opened, and the
audit above starts checking that. Off is the honest default.

Client-side tools (WhatsApp, Booking.com, spreadsheets) plug into `Agent.tools`
plus a `tool_use` handler in `Agent.send`. None are built — they need real
credentials and the Booking.com question in `state/projects.md` is still
`[UNKNOWN]`.

## Model settings, and why

- `claude-opus-5`, adaptive thinking (on by default), `effort=high`.
- **Server-side fallbacks** (`fallbacks="default"`): a safety-classifier
  decline is re-served by Anthropic's recommended fallback model inside the
  same call, so a benign question near a sensitive topic doesn't dead-end. If
  the fallback declines too, the run raises rather than pretending.
- **Prompt caching** on each agent's system prompt. It is byte-identical every
  turn, so it caches; the conversation grows after it and stays out of the
  prefix. This is why `Agent.system` is built once in the constructor.
- **Streaming**, because `max_tokens=32000` would otherwise risk an HTTP
  timeout.
- No `temperature` or `top_p` — rejected on this model. Steer with the prompt.

## Where this goes

The blocks are already the message schema. Porting to LangGraph means each
`Agent` becomes a node and `blocks()` becomes the edge condition — the agent
files still don't change.
