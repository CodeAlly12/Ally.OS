#!/usr/bin/env python3
"""Assemble paste-ready Custom GPT instruction files.

A Custom GPT has one Instructions field, so each agent needs its prompt and
its slice of the protocol concatenated into a single text. The field caps at
8,000 characters and the full PROTOCOL.md does not fit alongside an agent
file, so each agent gets only the blocks it actually emits or reads.

Run from the repo root: python3 deploy/custom-gpt/build.py
Regenerate whenever PROTOCOL.md or an agent file changes — these outputs are
derived, never edited by hand.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "deploy" / "custom-gpt"
LIMIT = 8000

# Which protocol blocks each agent needs in front of it. Chief of Staff needs
# all four: it emits three and reads the fourth.
AGENTS = {
    "chief_of_staff": ["TASK BRIEF", "RESULT PACKET", "DECISION REQUIRED", "STATE DIFF"],
    "research_analyst": ["TASK BRIEF", "RESULT PACKET"],
    "engineering_lead": ["TASK BRIEF", "RESULT PACKET"],
    "knowledge_manager": ["TASK BRIEF", "RESULT PACKET", "STATE DIFF"],
}

USAGE = {
    "chief_of_staff": (
        "I emit TASK BRIEF, DECISION REQUIRED, and STATE DIFF. I read RESULT\n"
        "PACKETs that Ally pastes back to me."
    ),
    "research_analyst": "I read TASK BRIEFs and emit RESULT PACKETs.",
    "engineering_lead": "I read TASK BRIEFs and emit RESULT PACKETs.",
    "knowledge_manager": (
        "I read TASK BRIEFs and emit STATE DIFFs, or a RESULT PACKET when the\n"
        "brief asks me to retrieve rather than write."
    ),
}


def section(protocol: str, heading_starts: str) -> str:
    """Return the body of the '## N. <name>' section starting with that text."""
    pattern = rf"^## \d+\. {re.escape(heading_starts)}.*?$(.*?)(?=^## |\Z)"
    match = re.search(pattern, protocol, re.M | re.S)
    if not match:
        sys.exit(f"section not found: {heading_starts}")
    return match.group(1).strip()


def blocks(protocol: str) -> dict:
    """Map each fenced template to its first line, e.g. 'TASK BRIEF'."""
    found = {}
    for body in re.findall(r"^```\n(.*?)^```", protocol, re.M | re.S):
        found[body.strip().splitlines()[0].strip()] = body.rstrip()
    return found


def main() -> int:
    protocol = (ROOT / "PROTOCOL.md").read_text()
    tags = section(protocol, "Claim tags")
    conventions = section(protocol, "Conventions")
    templates = blocks(protocol)

    over = []
    for name, wanted in AGENTS.items():
        agent = (ROOT / "agents" / f"{name}.md").read_text().strip()
        # The H1 is the file's title, not an instruction — drop it.
        agent = re.sub(r"\A# .*?\n+", "", agent)
        # A Custom GPT has no repo to read, so point at the appended section
        # instead of a filename that will not resolve.
        agent = re.sub(
            r"I follow `PROTOCOL\.md`\.\s+Where this file and the protocol disagree,"
            r"\s+the\s+protocol wins\.",
            "I follow the Protocol section below. Where these instructions and\n"
            "the protocol disagree, the protocol wins.",
            agent,
        )
        agent = agent.replace("`PROTOCOL.md`", "the Protocol section below")

        parts = [
            agent,
            "## Protocol",
            "This is the AllyOS wire format. Ally is the message bus: agents\n"
            "never call each other, they emit blocks that Ally copies into\n"
            "another chat window. Blocks go last in a message, after the prose.",
            USAGE[name],
            "### Claim tags",
            tags,
            "### Block formats",
            "Copy these exactly. Ally should never edit a block to paste it.",
        ]
        for block in wanted:
            if block not in templates:
                sys.exit(f"block template not found in PROTOCOL.md: {block}")
            parts.append(f"```\n{templates[block]}\n```")
        parts += ["### Conventions", conventions]

        text = "\n\n".join(parts) + "\n"
        path = OUT / f"{name}.txt"
        path.write_text(text)

        size = len(text)
        flag = "OVER LIMIT" if size > LIMIT else f"{LIMIT - size} spare"
        print(f"{path.relative_to(ROOT)}: {size} chars ({flag})")
        if size > LIMIT:
            over.append(name)

    if over:
        print(f"\n{len(over)} file(s) exceed the {LIMIT}-character Custom GPT "
              f"instruction limit: {', '.join(over)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
