#!/usr/bin/env python3
# Claude Code hook, run after every Bash command. When the command cut its own
# output, it adds one line to what the agent reads, saying so. It never blocks:
# most cuts are harmless looking around. The harm is the claim made from a cut
# ("none", "all", "passed"), and the habit fires hours after the instructions
# were read, so the reminder has to arrive with the output.
#
# In Josh's agents' history, 52% of Claude's shell commands cut their output
# (10 to 17 Nov 2026) and 17% of those also counted what they cut.
import json
import re
import sys

# Where a command name can start: the start, or after | ; & ( ` or a new line.
COMMAND_START = r"(?:^|[|;&(`\n])\s*(?:command\s+|xargs\s+(?:-\S+\s+)*)?"

WAYS_A_COMMAND_CUTS_ITS_OUTPUT = [
    COMMAND_START + r"(head\b(?:\s+-\S+|\s+\d+)*)",
    COMMAND_START + r"(tail\b(?!\s+-[a-zA-Z]*[fF])(?:\s+-\S+|\s+\d+)*)",
    COMMAND_START + r"(sed\s+(?:-[a-zA-Z]+\s+)*-[a-zA-Z]*n\b(?:\s+'[^']{0,40}'|\s+\"[^\"]{0,40}\"|\s+[^\s|;&]{1,40})?)",
    COMMAND_START + r"(cut\s+(?:-\S+\s+)*-[cb]\s*\S+)",
    COMMAND_START + r"((?:grep|egrep|fgrep|rg)\s+(?:[^|;&\n]*?\s)?-[a-zA-Z]*v[a-zA-Z]*\b)",
    COMMAND_START + r"((?:grep|egrep|fgrep|rg)\s+(?:[^|;&\n]*?\s)?--invert-match\b)",
    COMMAND_START + r"((?:grep|egrep|fgrep|rg)\s+(?:[^|;&\n]*?\s)?(?:-[a-zA-Z]*m\s*\d+|--max-count[= ]\d+))",
    COMMAND_START + r"(awk\s+(?:-\S+\s+\S+\s+)*'[^']*\bNR\s*(?:[<>=!%]|==)[^']{0,30})",
    r"(2>\s*/dev/null)",
    r"(\|\|\s*(?:true|:)(?=\s|;|$|\)))",
]


def ways_this_command_cut_its_output(command):
    found = []
    for pattern in WAYS_A_COMMAND_CUTS_ITS_OUTPUT:
        for match in re.finditer(pattern, command):
            way = " ".join(match.group(1).split())[:40]
            if way not in found:
                found.append(way)
    return found


def main():
    event = json.load(sys.stdin)
    if event.get("tool_name") != "Bash":
        return
    ways = ways_this_command_cut_its_output((event.get("tool_input") or {}).get("command") or "")
    if not ways:
        return
    reminder = (
        "Cut output (" + ", ".join(ways[:5]) + "): you are reading a sample, and what it hid looks the same as "
        "what isn't there. Before you say all, none, only, not found, passed or clean, get the fact itself: "
        "the count, the exit code, the whole file, the errors."
    )
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": reminder}}))


if __name__ == "__main__":
    main()
