# Run — 2026-08-04 — Villa booking assistant

Agents: Chief of Staff, Research Analyst. Ally is the message bus; each block
below was copied by hand from one chat window into another.

---

### Ally → Chief of Staff

I want to build an AI booking assistant for the Malindi villa portfolio.

---

### Chief of Staff → Ally

Objective as I read it: cut the hours you lose to guest enquiries without
losing bookings to slow replies. "AI booking assistant" is one possible
answer to that, not the objective itself.

One question, because it changes what we can build: do enquiries reach you
mainly on WhatsApp, or through the Airbnb and Booking.com inboxes?

---

### Ally → Chief of Staff

Mostly WhatsApp. Some Booking.com. No channel manager — spreadsheets and the
platform apps.

---

### Chief of Staff → Ally

No channel manager means no single system to integrate with, which decides
most of the cost. Research first.

```
TASK BRIEF
To: Research Analyst
Objective: Establish what can and cannot be automated in guest enquiry replies for a small Malindi villa portfolio, given no channel manager.
Why it matters: Ally is choosing between assisted replies and full auto-reply. Platform rules, not engineering, may decide it.
Context supplied: [VERIFIED — Ally, this session] Enquiries arrive mainly via WhatsApp, some via Booking.com. [VERIFIED — Ally, this session] No channel manager or PMS; bookings tracked in spreadsheets.
Deliverable: RESULT PACKET, findings tagged, covering platform messaging rules, integration requirements, and what determines whether automation pays.
Constraints: No live retrieval assumed — tag accordingly. Kenya/coastal context. Ally builds solo.
Done when: Every finding is tagged, and the largest unknown is named rather than estimated around.
Not in scope: Effort estimates, architecture, pricing strategy, guest data handling.
```

---

### Research Analyst → Chief of Staff

```
RESULT PACKET
From: Research Analyst
Objective as understood: Determine what blocks or permits automated replies to villa guest enquiries on WhatsApp and Booking.com, with no channel manager in place.
Findings:
- [UNKNOWN] Whether Booking.com currently grants messaging API access to a property of this size, or only to connectivity partners. This is the finding that decides the whole question and I cannot settle it without reading their current partner terms.
- [INFERRED — from training data, may be stale] Booking.com messaging has historically been reachable only through its Connectivity Partner programme, which assumes a channel manager in between. A solo operator is not the intended integrator.
- [INFERRED — from training data, may be stale] The WhatsApp Business API permits free-form replies only inside a 24-hour window after a guest's message; outbound outside it needs pre-approved templates. Enquiry replies usually fall inside that window, so this is workable.
- [INFERRED — from WhatsApp Business tiering as of 2024] The Business App is single-device and not automatable; the API route requires a Business Solution Provider, which is a signup step, not a build step.
- [UNKNOWN] Ally's weekly enquiry volume. Below roughly 20 a week, drafting assistance saves more per hour invested than any integration; above it, the integration starts to pay. I have no figure.
- [INFERRED — from the two findings above] Assisted drafting on WhatsApp is available today with no permissions gate; anything spanning both channels is blocked on the Booking.com unknown.
Confidence: 55% — no live retrieval in this session, so every platform-specific rule above is recalled, not checked, and platform terms change often.
What I could not determine: Booking.com's current API eligibility, and the enquiry volume that decides whether this pays. The first needs their partner documentation; the second needs Ally counting one week of messages.
Recommended next action: Have Ally count one week of enquiries by channel before any build is scoped.
Sources: none — no live retrieval available in this session.
```

---

### Chief of Staff → Ally

Research landed at 55%. Nothing claimed `[VERIFIED]`, so nothing to demote —
treat the platform rules as recalled, not checked. The load-bearing
unknown is Booking.com access, and it only blocks the option you'd want last.

```
DECISION REQUIRED
Decision: What shape is v1 of the booking assistant?
Options:
  A) WhatsApp assisted replies — agent drafts, you send — effort: S, 2-3 days — risk: saves less time than full automation
  B) Auto-reply across WhatsApp and Booking.com — effort: L, unbounded — risk: blocked on Booking.com API eligibility [UNKNOWN]; could stall at day one
  C) No software — fix canned templates and a response-time rule first — effort: S, half a day — risk: leaves the hours on the table
Recommendation: A — it captures most of the saving with no permissions gate, and you keep your hand on the send button while volume is small. B is the real product, but building it before the Booking.com unknown resolves is buying a maybe.
Default if you say nothing: A, starting with one week of enquiry counts.
Reversibility: A's drafting prompts survive into B unchanged; only the send path is thrown away.
```

---

## Acceptance check

1. **Blocks copy-pasteable as-is** — pass. Three blocks, each a plain fence,
   fields per `PROTOCOL.md`. No block needs editing to move between chats.
2. **Every Result Packet claim tagged, at least one honest `[UNKNOWN]`** —
   pass. Six findings, six tags, two `[UNKNOWN]` — and the first of them is
   the finding that decides the question, placed first per the agent's method.
3. **A decision, not a summary** — pass. Three genuinely different bets, one
   recommendation with reasoning, a default on silence, and the reversibility
   cost.
4. **Chief of Staff output under 400 words** — pass at 394, counting every
   word Ally reads: all prose plus the `TASK BRIEF` and `DECISION REQUIRED`
   blocks. It first came in at 412 and the prose was cut, not the blocks.

No `STATE DIFF` appears above because the session has not closed — Chief of
Staff is waiting on Ally's answer. The diff ships when Ally responds, and
`state/projects.md` already carries the resulting entry.
