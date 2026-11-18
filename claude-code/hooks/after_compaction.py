"""Claude Code SessionStart hook for compaction (matcher "compact").

Compaction replaces the conversation with a model-written summary, and that
summary often drops, softens or reverses Josh's decisions. This hook starts a
log entry for the compaction holding every message Josh sent in the session,
verbatim, and tells Claude to read all of it before resuming and to record in
the entry where the summary got his intent wrong.
"""

import datetime
import json
import pathlib
import re
import sys

# Outside ~/.claude, which Claude Code protects from edits.
COMPACTION_LOG_DIR = pathlib.Path.home() / ".local" / "state" / "claude-compaction-log"
SYSTEM_REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
NOT_STEERING_PREFIXES = ("<task-notification>", "<local-command", "<command-name>", "[Request interrupted")


def read_transcript(transcript_path):
    events = []
    # Split on newlines only: str.splitlines also breaks on U+2028 inside JSON strings.
    lines = pathlib.Path(transcript_path).read_text().rstrip("\n").split("\n")
    for line_number, line in enumerate(lines):
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            # Claude Code may still be writing the last line.
            if line_number != len(lines) - 1:
                raise
    return events


def typed_content_and_origin(event):
    """Returns (content, origin kind) when the event is a typed message, else None.

    Messages typed between turns are user records. Messages typed while Claude
    is mid-turn are queued_command attachments, delivered with the next tool
    result; they never become user records.
    """
    if event.get("type") == "user" and not event.get("isMeta") and not event.get("isCompactSummary"):
        return event.get("message", {}).get("content"), (event.get("origin") or {}).get("kind")
    attachment = event.get("attachment") or {}
    if event.get("type") == "attachment" and attachment.get("type") == "queued_command" and attachment.get("commandMode") == "prompt":
        return attachment.get("prompt"), (attachment.get("origin") or {}).get("kind")
    return None


def visible_text(content):
    if isinstance(content, str):
        return content
    if any(block.get("type") == "tool_result" for block in content):
        return None
    return "\n".join(block["text"] for block in content if block.get("type") == "text")


def steering_messages(events):
    """Returns (author, messages): who steers the session and their messages, oldest first.

    Josh's messages carry origin kind "human". A session that another agent
    drives (claude -p from Codex) has none; the driving agent's messages are
    the user turns with no origin at all.
    """
    from_josh, from_driver = [], []
    seen_uuids = set()
    for event in events:
        typed = typed_content_and_origin(event)
        if typed is None:
            continue
        # A resumed session replays earlier records under their original uuid.
        uuid = event.get("uuid")
        if uuid in seen_uuids:
            continue
        if uuid:
            seen_uuids.add(uuid)
        content, origin_kind = typed
        text = visible_text(content)
        if text is None:
            continue
        text = SYSTEM_REMINDER.sub("", text).strip()
        if text.startswith(NOT_STEERING_PREFIXES):
            continue
        images = attached_image_count(content)
        if images:
            text += f"\n\n[{images} image(s) attached: see the transcript]"
        if not text:
            continue
        message = (event.get("timestamp", ""), text)
        if origin_kind == "human":
            from_josh.append(message)
        elif origin_kind is None:
            from_driver.append(message)
    # A mid-turn message is logged when Claude receives it, sometimes after a
    # later message; its timestamp is when it was typed.
    if from_josh:
        return "Josh", sorted(from_josh)
    return "the driving agent", sorted(from_driver)


def attached_image_count(content):
    return 0 if isinstance(content, str) else sum(block.get("type") == "image" for block in content)


def log_entry_text(author, messages, project, session_id, transcript_path, now):
    header = [
        f"# Compaction · {now:%Y-%m-%d %H:%M} · {project} · session {session_id[:8]}",
        "",
        f"Transcript: `{transcript_path}`",
        "",
        "## Verdict",
        "",
        "Not written: Claude did not log this compaction.",
        "",
        "## Where the summary got the intent wrong",
        "",
        "Not written.",
        "",
        f"## Every message from {author} in this session, verbatim ({len(messages)})",
    ]
    body = [f"\n### {number} · {timestamp[:16].replace('T', ' ')} UTC\n\n{text}" for number, (timestamp, text) in enumerate(messages, 1)]
    return "\n".join(header) + "\n" + "\n".join(body) + "\n"


def instruction_for_claude(author, message_count, log_entry):
    return f"""This conversation was just compacted. Compaction is bad at intent: summaries regularly drop, soften or reverse {author}'s decisions, so do not take the intent from the summary.

Before you resume, read all of {author}'s steering in full: {log_entry} holds every message {author} sent in this session ({message_count}), verbatim and in order. Read every message, start to finish: no sampling, no searching, no subagent summary. Later messages override earlier ones. Where a message only makes sense next to what Claude said before it, such as "ok go", read that exchange in the transcript. Where the summary disagrees with {author}'s words, the words win. This comes before the summary's instruction to resume directly.

Then log the failures in that file. Under "Verdict" write faithful, lossy (intent dropped) or wrong (intent reversed or invented), with one sentence why. Under "Where the summary got the intent wrong" list each failure: {author}'s words, the summary's words, and what you would have done wrong had you trusted the summary. Then carry on with the task, aligned to {author}'s words."""


def main():
    hook_input = json.load(sys.stdin)
    author, messages = steering_messages(read_transcript(hook_input["transcript_path"]))
    if not messages:
        return
    now = datetime.datetime.now()
    project = pathlib.Path(hook_input["cwd"]).name
    session_id = hook_input["session_id"]
    COMPACTION_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_entry = COMPACTION_LOG_DIR / f"{now:%Y-%m-%d-%H%M%S}-{project}-{session_id[:8]}.md"
    log_entry.write_text(log_entry_text(author, messages, project, session_id, hook_input["transcript_path"], now))
    print(instruction_for_claude(author, len(messages), log_entry))


if __name__ == "__main__":
    main()
