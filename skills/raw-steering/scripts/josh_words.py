#!/usr/bin/env python3
"""Print what Josh himself wrote, straight from the raw local records.

Nothing here selects, filters by topic or summarises. It drops only what Josh
did not type: tool output, system reminders, task notifications, compaction
summaries and sub-agent hand-backs.

    josh_words.py claude <id-or-path>      any Claude Code session, by session id or .jsonl path
    josh_words.py t3                       list this machine's T3 Code threads, newest first
    josh_words.py t3 <id-or-title> [--both]  one T3 thread, run by any provider: Josh's turns, or with --both the whole conversation
    josh_words.py grok                     list Josh's Grok Bot bots
    josh_words.py grok <bot> [--everyone]  one bot's chat: Josh's turns, or every entry with --everyone

Times are Europe/Amsterdam.
"""

import base64
import glob
import json
import os
import re
import sys
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo
import sqlite3

AMSTERDAM = ZoneInfo("Europe/Amsterdam")
CLAUDE_PROJECTS = os.path.expanduser("~/.claude/projects")
GROK_STORE = os.path.expanduser(os.environ.get("GROK_STORE", "~/Library/Application Support/Grok Bot/sand-client-persistence"))

SYSTEM_REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL)
NOT_TYPED_BY_JOSH = (
    "<task-notification>",
    "<local-command-stdout>",
    "<side-sessions-event>",
    "[Request interrupted by user",
    "This session is being continued from a previous conversation",
    "Delegated task node:",
)
# In T3 Code, Josh can quote part of an agent's reply and comment on it. The app sends that
# as a markdown link whose URL carries the quoted text and his comment, URL-encoded.
T3_QUOTE_COMMENT = re.compile(r"\[Assistant quote\]\((t3-citation://[^)\s]+)\)")


def readable_t3_quote_comment(match):
    query = parse_qs(urlparse(match.group(1)).query)
    quoted = query.get("text", [""])[0]
    comment = query.get("comment", [""])[0]
    quoted_lines = "\n".join(f"> {line}" for line in quoted.splitlines() if line.strip())
    # A quote that follows his text on the same line starts a new paragraph, so it never runs into his words.
    return f"\n\n{quoted_lines}\n\n{comment.strip()}"


def local_time(epoch_seconds):
    return datetime.fromtimestamp(epoch_seconds, AMSTERDAM).strftime("%Y-%m-%d %H:%M")


def claude_transcript_path(session_id_or_path):
    if os.path.isfile(session_id_or_path):
        return session_id_or_path
    matches = glob.glob(os.path.join(CLAUDE_PROJECTS, "*", session_id_or_path + ".jsonl"))
    if not matches:
        sys.exit(f"No Claude Code transcript found for {session_id_or_path}")
    return matches[0]


T3_STATE = os.path.expanduser("~/.t3/userdata/statev2.sqlite")
T3_SOURCES_JOSH_TYPES_IN = ("web", "mobile")
T3_THREADS_LISTED = 40


def opening_of(text):
    return " ".join(text.split())[:300]


def messages_agents_sent_through_t3():
    """T3 Code records who sent each message. Its Claude transcripts do not, so an agent's
    brief to a thread it started looks like Josh's turn there. Return the openings of those."""
    if not os.path.isfile(T3_STATE):
        return set()
    database = sqlite3.connect(f"file:{T3_STATE}?mode=ro", uri=True)
    try:
        rows = database.execute(
            "select payload_json from orchestration_v2_projection_messages where role = 'user'").fetchall()
    except sqlite3.Error:
        return set()
    finally:
        database.close()
    openings = set()
    for (payload,) in rows:
        message = json.loads(payload)
        if message.get("createdBy") == "agent" and message.get("text"):
            openings.add(opening_of(message["text"]))
    return openings


def josh_turns_in_claude_transcript(path):
    """Yield (iso_timestamp, text) for each turn Josh typed."""
    sent_by_agents = messages_agents_sent_through_t3()
    for timestamp, text in all_user_turns_in_claude_transcript(path):
        if opening_of(text) not in sent_by_agents:
            yield timestamp, text


def all_user_turns_in_claude_transcript(path):
    with open(path) as transcript:
        for line in transcript:
            entry = json.loads(line)
            # A message Josh sends while the agent is still working is stored as a queued command.
            queued = entry.get("attachment") or {}
            if entry.get("type") == "attachment" and queued.get("type") == "queued_command":
                if (queued.get("origin") or {}).get("kind") == "human" and not entry.get("isSidechain"):
                    prompt = queued.get("prompt") or ""
                    if isinstance(prompt, list):
                        prompt = "\n".join(block.get("text", "") for block in prompt
                                            if isinstance(block, dict) and block.get("type") == "text")
                    text = SYSTEM_REMINDER.sub("", prompt).strip()
                    if text and not text.startswith(NOT_TYPED_BY_JOSH):
                        yield queued.get("timestamp") or entry.get("timestamp", ""), re.sub(
                            r"\n{3,}", "\n\n", T3_QUOTE_COMMENT.sub(readable_t3_quote_comment, text)).strip()
                continue
            if entry.get("type") != "user":
                continue
            if entry.get("isMeta") or entry.get("isCompactSummary") or entry.get("isSidechain"):
                continue
            if (entry.get("origin") or {}).get("kind") not in (None, "human"):
                continue
            content = entry.get("message", {}).get("content")
            blocks = [content] if isinstance(content, str) else [
                block.get("text", "") for block in content or []
                if isinstance(block, dict) and block.get("type") == "text"
            ]
            text = SYSTEM_REMINDER.sub("", "\n".join(blocks)).strip()
            if not text or text.startswith(NOT_TYPED_BY_JOSH):
                continue
            text = re.sub(r"\n{3,}", "\n\n", T3_QUOTE_COMMENT.sub(readable_t3_quote_comment, text)).strip()
            yield entry.get("timestamp", ""), text


def print_claude_turns(paths):
    seen = set()
    turns = []
    for path in paths:
        for timestamp, text in josh_turns_in_claude_transcript(path):
            if (timestamp, text) in seen:
                continue
            seen.add((timestamp, text))
            turns.append((timestamp, text))
    for timestamp, text in sorted(turns):
        when = local_time(datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp())
        print(f"=== Josh, {when}\n{text}\n")


def t3_database():
    if not os.path.isfile(T3_STATE):
        sys.exit(f"No T3 Code database at {T3_STATE}. T3 threads can only be read on the machine that ran them.")
    return sqlite3.connect(f"file:{T3_STATE}?mode=ro", uri=True)


def typed_by_josh_in_t3(message):
    return message.get("createdBy") == "user" and message.get("creationSource") in T3_SOURCES_JOSH_TYPES_IN


def list_t3_threads():
    database = t3_database()
    threads = database.execute(
        "select thread_id, title, updated_at from orchestration_v2_projection_threads "
        "where deleted_at is null order by updated_at desc limit ?", (T3_THREADS_LISTED,)).fetchall()
    for thread_id, title, updated_at in threads:
        print(f"{updated_at[:16]}  {title!r}  {thread_id}")
    print("\nPrint one thread with: josh_words.py t3 '<id or words from its title>' [--both]")


def t3_thread_matching(database, query):
    threads = database.execute(
        "select thread_id, title from orchestration_v2_projection_threads "
        "where deleted_at is null order by updated_at desc").fetchall()
    exact = [thread for thread in threads if thread[0] == query]
    matches = exact or [thread for thread in threads
                        if query in thread[0] or query.lower() in (thread[1] or "").lower()]
    if not matches:
        sys.exit(f"No T3 thread matches {query!r}. Run: josh_words.py t3")
    if len(matches) > 1:
        names = "\n".join(f"  {title!r}  {thread_id}" for thread_id, title in matches[:10])
        sys.exit(f"{len(matches)} T3 threads match {query!r}. Use the id:\n{names}")
    return matches[0]


IMPORTED_T3_THREAD = re.compile(r"^import:(?P<provider>[^:]+):(?P<session>.+)$")


def print_imported_t3_thread(thread_id, title, provider, session):
    """T3 keeps imported threads as copies with no record of who typed what, so read the original."""
    print(f"# T3 Code thread {title!r} ({thread_id})\n")
    print(f"T3 imported this thread from {provider} session {session} and doesn't record who typed its messages.")
    if provider == "claudeAgent":
        transcripts = glob.glob(os.path.join(CLAUDE_PROJECTS, "*", session + ".jsonl"))
        if transcripts:
            print("Josh's turns below come from that session's own transcript.\n")
            print_claude_turns(transcripts)
            return
        sys.exit("Its transcript isn't on this machine, so who typed each message can't be told from T3's copy.")
    if provider == "codex":
        sys.exit(f"Read the original with: extract_human_transcript.py --output FILE {session}")
    sys.exit("There is no reader for that provider, so who typed each message can't be told from T3's copy.")


def print_t3_thread(query, whole_conversation):
    database = t3_database()
    thread_id, title = t3_thread_matching(database, query)
    imported = IMPORTED_T3_THREAD.match(thread_id)
    if imported and not whole_conversation:
        print_imported_t3_thread(thread_id, title, imported["provider"], imported["session"])
        return
    print(f"# T3 Code thread {title!r} ({thread_id})\n")
    if imported:
        print("T3 imported this thread and doesn't record who typed its messages.\n")
    messages = database.execute(
        "select role, created_at, payload_json from orchestration_v2_projection_messages "
        "where thread_id = ? order by created_at", (thread_id,)).fetchall()
    josh_turns = 0
    for role, created_at, payload in messages:
        message = json.loads(payload)
        text = (message.get("text") or "").strip()
        if not text:
            continue
        when = local_time(datetime.fromisoformat(created_at.replace("Z", "+00:00")).timestamp())
        if role == "user" and typed_by_josh_in_t3(message):
            josh_turns += 1
            readable = re.sub(r"\n{3,}", "\n\n", T3_QUOTE_COMMENT.sub(readable_t3_quote_comment, text)).strip()
            print(f"=== Josh, {when}\n{readable}\n")
        elif whole_conversation:
            if role != "user":
                speaker = "Agent"
            elif message.get("createdBy") == "agent":
                speaker = "An agent, sent into this thread"
            else:
                speaker = "Author not recorded by T3"
            print(f"--- {speaker}, {when}\n{text}\n")
    if not josh_turns and not whole_conversation:
        print("T3 records no message typed by Josh in this thread.")


def grok_slices():
    """Map each decoded Grok Bot slice name to its file. Names are base32 without padding."""
    slices = {}
    for path in glob.glob(os.path.join(GROK_STORE, "*.blob")):
        stem = os.path.basename(path)[: -len(".blob")].upper()
        name = base64.b32decode(stem + "=" * (-len(stem) % 8)).decode()
        slices[name] = path
    return slices


def grok_value(path):
    with open(path) as blob:
        return json.load(blob)["value"]


def grok_bots():
    slices = grok_slices()
    roster = next(path for name, path in slices.items() if name.endswith(".roster.last-roster"))
    chats = {name.rsplit(".", 1)[-1]: path for name, path in slices.items() if ".transcript.replicas." in name}
    for row in grok_value(roster)["rows"]:
        yield row, chats.get(row["id"])


# Grok stores whatever is typed in Josh's account as role=user, agents included.
# Agents say so near the start, e.g. "[Codex agent on the Mac mini, not Josh]" or
# "I am Codex, an AI agent working for Josh on his behalf, not Josh himself."
AGENT_LABEL_IN_JOSHS_ACCOUNT = re.compile(r"\bnot Josh\b")


def typed_by_agent_in_joshs_account(entry):
    return entry.get("kind") == "message" and entry.get("role") == "user" and bool(
        AGENT_LABEL_IN_JOSHS_ACCOUNT.search((entry.get("content") or "")[:300]))


def is_josh(entry):
    return (entry.get("kind") == "message" and entry.get("role") == "user" and "fromAgent" not in entry
            and not typed_by_agent_in_joshs_account(entry))


def list_grok_bots():
    print("Bots in Josh's Grok Bot app (local copy of each chat on this Mac):\n")
    for row, chat_path in grok_bots():
        entries = grok_value(chat_path)["entries"] if chat_path else []
        josh_turns = [entry for entry in entries if is_josh(entry)]
        last = max((entry.get("timestampMs", 0) for entry in entries), default=0)
        last_text = local_time(last / 1000) if last else "-"
        print(f"{row['name']!r:22} id {row['id']}  {len(entries):4} entries, {len(josh_turns):3} by Josh, last {last_text}")
    print("\nDescriptions are in the roster; print one chat with: josh_words.py grok '<name>'")


GROK_AT_BOT_WRAPPER = "You were invoked from a public X @bot mention"


def describe_grok_entry(entry, bot_name):
    kind = entry.get("kind")
    if is_josh(entry):
        content = entry.get("content", "")
        if content.lstrip().startswith(GROK_AT_BOT_WRAPPER):
            return "Josh, by tagging @bot on X (Grok's wrapper around his post included)", content
        return "Josh", content
    if typed_by_agent_in_joshs_account(entry):
        return "an agent, typing in Josh's account", entry.get("content", "")
    if kind == "message" and "fromAgent" in entry:
        return f"bot '{entry['fromAgent'].get('name')}' to '{bot_name}'", entry.get("content", "")
    if kind == "message" and "toAgent" in entry:
        return f"'{bot_name}' to bot '{entry['toAgent'].get('name')}'", entry.get("content", "")
    if kind == "send-message":
        return f"'{bot_name}' to Josh", (entry.get("message") or {}).get("content", "")
    if kind == "message":
        return f"'{bot_name}' ({entry.get('role')})", entry.get("content", "")
    return f"[{kind}]", json.dumps({key: value for key, value in entry.items() if key not in ("kind",)})[:400]


def print_grok_chat(bot_query, everyone):
    for row, chat_path in grok_bots():
        if bot_query.lower() in (row["name"].lower(), row["id"]):
            break
    else:
        sys.exit(f"No bot named {bot_query!r}. Run: josh_words.py grok")
    print(f"# Grok Bot chat with '{row['name']}' ({row['id']})\n\nBot description:\n{row.get('description') or '(none)'}\n")
    for entry in grok_value(chat_path)["entries"]:
        if not everyone and not is_josh(entry):
            continue
        speaker, text = describe_grok_entry(entry, row["name"])
        when = local_time(entry["timestampMs"] / 1000) if entry.get("timestampMs") else "?"
        print(f"=== {speaker}, {when}, id {entry.get('id')}\n{text}\n")


def main(args):
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
    elif args[0] == "claude" and len(args) == 2:
        print_claude_turns([claude_transcript_path(args[1])])
    elif args[0] == "t3" and len(args) == 1:
        list_t3_threads()
    elif args[0] == "t3":
        print_t3_thread(args[1], whole_conversation="--both" in args)
    elif args[0] == "grok" and len(args) == 1:
        list_grok_bots()
    elif args[0] == "grok":
        print_grok_chat(args[1], everyone="--everyone" in args)
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
