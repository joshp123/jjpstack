#!/usr/bin/env python3
"""Print a Claude Code session as Josh read it: his turns and the agent's replies, word for word.

Josh's turns come from josh_words.py beside this file, so both tools agree on what Josh typed. The agent's replies are its text and the cards the Claude desktop
app showed him: end-of-turn recaps, questions with their buttons, and offers to start a session.
Tool calls, tool output and the agent's thinking are left out. The app also showed him the
thinking, and he sometimes quotes it; his quote is then in his turn. Nothing is summarised or
reworded.

    conversation.py <session-id-or-path>

Times are Europe/Amsterdam.
"""

import importlib.util
import json
import os
import sys
from datetime import datetime

READER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "josh_words.py")
reader_spec = importlib.util.spec_from_file_location("josh_words", READER_PATH)
josh_words = importlib.util.module_from_spec(reader_spec)
reader_spec.loader.exec_module(josh_words)


def local_time(iso_timestamp):
    return josh_words.local_time(datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00")).timestamp())


def card_shown_by_desktop_app(tool_use):
    """The text of a card the Claude desktop app drew from one of its own tools, or None."""
    name, card = tool_use.get("name", ""), tool_use.get("input") or {}
    if name.endswith("ccd_turn__wrap_up"):
        lines = [f"[Recap card] {card.get('recap', '')}"]
        if card.get("ask"):
            lines.append(f"[Question] {card['ask']}")
        for action in card.get("actions") or []:
            lines.append(f"[Button] {action.get('label')}: \"{action.get('message')}\"")
        return "\n".join(lines)
    if name.endswith("ccd_session__start_session"):
        return f"[Offer to start a session] {card.get('title', '')}"
    return None


def agent_replies_in_claude_transcript(path):
    """Yield (iso_timestamp, text) for each piece of text or app card the agent showed in the main thread."""
    with open(path) as transcript:
        for line in transcript:
            entry = json.loads(line)
            if entry.get("type") != "assistant" or entry.get("isSidechain"):
                continue
            shown = []
            for block in entry.get("message", {}).get("content") or []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text" and block.get("text", "").strip():
                    shown.append(block["text"].strip())
                elif block.get("type") == "tool_use" and card_shown_by_desktop_app(block):
                    shown.append(card_shown_by_desktop_app(block))
            if shown:
                yield entry.get("timestamp", ""), "\n".join(shown)


def main(args):
    if len(args) != 1 or args[0] in ("-h", "--help"):
        print(__doc__)
        return
    path = josh_words.claude_transcript_path(args[0])
    turns = [(timestamp, "Josh", text) for timestamp, text in josh_words.josh_turns_in_claude_transcript(path)]
    turns += [(timestamp, "Claude", text) for timestamp, text in agent_replies_in_claude_transcript(path)]
    for timestamp, speaker, text in sorted(turns):
        marker = "===" if speaker == "Josh" else "---"
        print(f"{marker} {speaker}, {local_time(timestamp)}\n{text}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
