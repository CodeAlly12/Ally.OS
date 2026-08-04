#!/usr/bin/env python3
"""AllyOS orchestration runtime.

Replaces Ally as the message bus. Loads the agent prompts from `agents/`,
runs them against the Claude API, parses the fenced blocks defined in
`PROTOCOL.md`, and routes them between agents automatically. The prompts and
the block formats are unchanged — this reads the same files a Claude Project
or a Custom GPT would.

Each agent keeps its own message history. That isolation is the point: a
specialist must not see Chief of Staff's framing, or a TASK BRIEF stops being
self-contained and the claim tags degrade into things the specialist "already
knows".

    python3 runtime/allyos.py "I want to build an AI booking assistant"
    python3 runtime/allyos.py --search "..."   # give Research Analyst the web

Needs ANTHROPIC_API_KEY, or an `ant auth login` profile.
"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys

import anthropic

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = "claude-opus-5"

# Server-side fallback: a policy decline is re-served by Anthropic's
# recommended fallback model inside the same call, rather than surfacing to us
# as an unanswered refusal.
FALLBACK_BETA = "server-side-fallback-2026-07-01"

BLOCK_NAMES = ("TASK BRIEF", "RESULT PACKET", "DECISION REQUIRED", "STATE DIFF")
SPECIALISTS = {
    "research analyst": "research_analyst",
    "engineering lead": "engineering_lead",
    "knowledge manager": "knowledge_manager",
}
# Sources vague enough that a [VERIFIED] tag citing them is a protocol
# violation, not a citation. See PROTOCOL.md §1.
VAGUE_SOURCES = ("industry", "reports", "research", "studies", "data", "sources", "web")


class Agent:
    """One agent: its prompt, its own history, its own tools."""

    def __init__(self, name: str, client: anthropic.Anthropic, tools: list | None = None):
        self.name = name
        self.client = client
        self.tools = tools or []
        agent_md = (ROOT / "agents" / f"{name}.md").read_text()
        protocol = (ROOT / "PROTOCOL.md").read_text()
        self.system = f"{agent_md}\n\n---\n\n{protocol}"
        self.messages: list[dict] = []

    def send(self, text: str, effort: str = "high") -> str:
        """One turn. Returns the agent's text output."""
        self.messages.append({"role": "user", "content": text})

        while True:  # re-enter on pause_turn (server tools hit their iteration cap)
            with self.client.beta.messages.stream(
                model=MODEL,
                max_tokens=32000,
                betas=[FALLBACK_BETA],
                fallbacks="default",
                # The prompt is byte-identical every turn, so it caches; the
                # conversation after it grows and is not part of the prefix.
                system=[{
                    "type": "text",
                    "text": self.system,
                    "cache_control": {"type": "ephemeral"},
                }],
                output_config={"effort": effort},
                tools=self.tools,
                messages=self.messages,
            ) as stream:
                response = stream.get_final_message()

            if response.stop_reason == "refusal":
                category = getattr(response.stop_details, "category", None)
                raise RuntimeError(
                    f"{self.name} refused (category: {category}). The fallback model "
                    "declined too — this needs a human, not a retry."
                )

            self.messages.append({"role": "assistant", "content": response.content})
            if response.stop_reason != "pause_turn":
                break

        return "".join(b.text for b in response.content if b.type == "text")


def blocks(text: str) -> list[tuple[str, str]]:
    """Extract fenced protocol blocks as (name, body) pairs, in order."""
    found = []
    for body in re.findall(r"^```[a-z]*\n(.*?)^```", text, re.M | re.S):
        first = body.strip().splitlines()[0].strip() if body.strip() else ""
        if first in BLOCK_NAMES:
            found.append((first, body.rstrip()))
    return found


def field(block: str, name: str) -> str | None:
    match = re.search(rf"^{re.escape(name)}:\s*(.+)$", block, re.M)
    return match.group(1).strip() if match else None


def route(brief: str) -> str:
    """Resolve a TASK BRIEF's `To:` line to an agent module name."""
    to = (field(brief, "To") or "").lower()
    for label, module in SPECIALISTS.items():
        if label in to:
            return module
    raise ValueError(f"TASK BRIEF addressed to an agent I don't have: {to!r}")


def audit_tags(packet: str, searched: bool) -> list[str]:
    """Flag [VERIFIED] tags that don't carry a source worth the name."""
    warnings = []
    for claim in re.findall(r"\[VERIFIED\s*—\s*([^\]]+)\]", packet):
        source = claim.strip().lower()
        if not searched:
            warnings.append(f"[VERIFIED — {claim.strip()}] with no live retrieval enabled")
        elif len(source.split()) < 3 and any(v in source for v in VAGUE_SOURCES):
            warnings.append(f"[VERIFIED — {claim.strip()}] cites nothing findable")
    if "[UNKNOWN]" not in packet:
        warnings.append("no [UNKNOWN] anywhere — suspicious on a hard question")
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an AllyOS session end to end.")
    parser.add_argument("objective", help="What you want, in your own words.")
    parser.add_argument("--search", action="store_true",
                        help="Give Research Analyst web search. Its [VERIFIED] tags "
                             "become meaningful — and auditable.")
    parser.add_argument("--effort", default="high",
                        choices=["low", "medium", "high", "xhigh", "max"])
    parser.add_argument("--max-rounds", type=int, default=6)
    parser.add_argument("--no-state", action="store_true",
                        help="Skip loading state/ (start Chief of Staff blind).")
    args = parser.parse_args()

    client = anthropic.Anthropic()
    search_tools = [{"type": "web_search_20260209", "name": "web_search"}]

    cos = Agent("chief_of_staff", client)
    made: dict[str, Agent] = {}

    def specialist(module: str) -> Agent:
        if module not in made:
            tools = search_tools if (args.search and module == "research_analyst") else []
            made[module] = Agent(module, client, tools=tools)
        return made[module]

    if args.no_state:
        opening = f"no state\n\n{args.objective}"
    else:
        projects = (ROOT / "state" / "projects.md").read_text()
        decisions = (ROOT / "state" / "decisions.md").read_text()
        opening = f"{projects}\n\n{decisions}\n\n{args.objective}"

    transcript = [f"# Run — {dt.date.today()} — {args.objective}", "",
                  f"Model: {MODEL}. Effort: {args.effort}. "
                  f"Live retrieval: {'on' if args.search else 'off'}.", "",
                  "---", "", "### Ally → Chief of Staff", "", args.objective]
    warnings: list[str] = []
    message, speaker = opening, cos

    for _ in range(args.max_rounds):
        reply = speaker.send(message, effort=args.effort)
        label = "Chief of Staff" if speaker is cos else speaker.name.replace("_", " ").title()
        target = "Ally" if speaker is cos else "Chief of Staff"
        transcript += ["", "---", "", f"### {label} → {target}", "", reply]
        print(f"\n=== {label} ===\n{reply}")

        emitted = blocks(reply)
        if not emitted:
            print("\n[No block emitted — the loop needs your answer.]")
            break

        name, body = emitted[-1]
        if name in ("DECISION REQUIRED", "STATE DIFF"):
            print(f"\n[{name} — over to you.]")
            break

        if name == "TASK BRIEF":
            speaker = specialist(route(body))
            message = f"```\n{body}\n```"
        elif name == "RESULT PACKET":
            found = audit_tags(body, searched=bool(speaker.tools))
            for w in found:
                print(f"[tag audit] {speaker.name}: {w}")
            warnings += [f"{speaker.name}: {w}" for w in found]
            speaker, message = cos, f"```\n{body}\n```"
    else:
        print(f"\n[Stopped at --max-rounds {args.max_rounds}.]")

    if warnings:
        transcript += ["", "---", "", "## Tag audit", ""]
        transcript += [f"- {w}" for w in warnings]

    slug = re.sub(r"[^a-z0-9]+", "-", args.objective.lower())[:40].strip("-")
    path = ROOT / "runs" / f"{dt.date.today()}-{slug}.md"
    path.write_text("\n".join(transcript) + "\n")
    print(f"\nRun saved: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
