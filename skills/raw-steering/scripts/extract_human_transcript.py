#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import subprocess
from pathlib import Path


THREAD_ID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
SERIALIZED_RECORD_TYPE_PATTERN = re.compile(
    r'^\s*\{\s*"timestamp"\s*:\s*"[^"]*"\s*,\s*"type"\s*:\s*"([^"]+)"\s*,'
)
CODEX_DELEGATION_PATTERN = re.compile(r"^\s*<codex_delegation(?:\s|>)")
T3_STATE = Path.home() / ".t3/userdata/statev2.sqlite"
# How the codex-subagent skill marks text an agent wrote into a chat.
AGENT_WRITTEN_OPENINGS = ("Task:", "[Agent-to-agent message")


def opening_of(text: str) -> str:
    return " ".join(text.split())[:300]


def openings_agents_sent_through_t3() -> set[str]:
    """T3 Code records who sent each message. A Codex rollout does not, so an agent's brief looks like a human's."""
    if not T3_STATE.is_file():
        return set()
    database = sqlite3.connect(f"file:{T3_STATE}?mode=ro", uri=True)
    try:
        rows = database.execute("select payload_json from orchestration_v2_projection_messages where role = 'user'").fetchall()
    except sqlite3.Error:
        return set()
    finally:
        database.close()
    return {opening_of(message["text"]) for message in map(json.loads, (row[0] for row in rows))
            if message.get("createdBy") == "agent" and message.get("text")}


SENT_BY_AGENTS_THROUGH_T3 = openings_agents_sent_through_t3()
# Threads a --project-root export had to leave out, with why, so a partial export never passes for the whole.
THREADS_NOT_READ: dict[str, str] = {}


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def normalize_thread_id(value: str) -> str:
    thread_id = value.removeprefix("codex://threads/").strip().lower()
    if not THREAD_ID_PATTERN.fullmatch(thread_id):
        fail(f"invalid Codex task ID: {value}")
    return thread_id


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract direct human messages from one or more Codex tasks."
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--project-root",
        type=Path,
        help="Also include every human Codex task whose working directory is in this repository or one of its worktrees.",
    )
    parser.add_argument("thread_ids", nargs="*")
    arguments = parser.parse_args()
    if not arguments.thread_ids and arguments.project_root is None:
        parser.error("give task IDs, --project-root, or both")
    return arguments


def project_directories(project_root: Path) -> list[str]:
    worktree_list = subprocess.run(
        ["git", "-C", str(project_root), "worktree", "list", "--porcelain"],
        capture_output=True, text=True, check=True,
    ).stdout
    directories = [line.removeprefix("worktree ") for line in worktree_list.splitlines() if line.startswith("worktree ")]
    return directories or [str(project_root.resolve())]


def human_project_thread_ids(codex_home: Path, project_root: Path) -> list[str]:
    # Structural selection only: human-started tasks run in the project's own
    # directories. Sub-agents and `codex exec` runs are agent prompts, not steering.
    database = sqlite3.connect(f"file:{codex_home / 'state_5.sqlite'}?mode=ro", uri=True)
    rows = database.execute(
        "select id, cwd from threads where source not like '{%' and source != 'exec' order by created_at"
    ).fetchall()
    directories = project_directories(project_root)
    return [
        thread_id for thread_id, cwd in rows
        if any(cwd == directory or cwd.startswith(directory + "/") for directory in directories)
    ]


def extract_thread(codex_home: Path, thread_id: str, required: bool = True) -> dict | None:
    rollout_paths = sorted(
        path
        for root in (codex_home / "sessions", codex_home / "archived_sessions")
        if root.exists()
        for path in root.rglob(f"*{thread_id}.jsonl")
    )
    if not rollout_paths:
        compressed = sorted(
            path
            for root in (codex_home / "sessions", codex_home / "archived_sessions")
            if root.exists()
            for path in root.rglob(f"*{thread_id}.jsonl.zst")
        )
        reason = (f"only a compressed archive exists, {compressed[0]}; decompress it with zstd -d to include it"
                  if compressed else "no rollout on this machine")
        if not required:
            THREADS_NOT_READ[thread_id] = reason
            return None
        fail(f"task {thread_id}: {reason}")

    user_messages = []

    for rollout_path in rollout_paths:
        source_bytes = rollout_path.read_bytes()
        found_matching_session_metadata = False
        inside_classified_malformed_record = False

        for line_number, line in enumerate(source_bytes.decode("utf-8").splitlines(), start=1):
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                serialized_record_match = SERIALIZED_RECORD_TYPE_PATTERN.match(line)
                if serialized_record_match is not None:
                    malformed_record_type = serialized_record_match.group(1)
                    if malformed_record_type in {"session_meta", "event_msg"}:
                        fail(
                            f"malformed trusted {malformed_record_type} record in "
                            f"{rollout_path} on line {line_number}"
                        )
                    inside_classified_malformed_record = True
                    continue
                if inside_classified_malformed_record:
                    continue
                fail(f"unclassified malformed record in {rollout_path} on line {line_number}")

            inside_classified_malformed_record = False

            if event.get("type") == "session_meta":
                session_payload = event.get("payload", {})
                if session_payload.get("id") == thread_id:
                    found_matching_session_metadata = True
                session_source = session_payload.get("source")
                if isinstance(session_source, dict) and "subagent" in session_source:
                    if not required:
                        return None
                    fail(f"task {thread_id} is a subagent task, not a human conversation")

            if event.get("type") != "event_msg":
                continue
            payload = event.get("payload", {})
            if payload.get("type") == "user_message":
                message = payload.get("message")
            elif payload.get("type") == "item_completed" and payload.get("item", {}).get("type") == "UserMessage":
                content = payload["item"].get("content")
                if not isinstance(content, list):
                    fail(f"malformed user content in {rollout_path} on line {line_number}")
                text_blocks = [block.get("text") for block in content if block.get("type") == "text"]
                if not all(isinstance(text, str) for text in text_blocks):
                    fail(f"malformed user text in {rollout_path} on line {line_number}")
                message = "\n".join(text_blocks)
            else:
                continue

            timestamp = event.get("timestamp")
            if not isinstance(timestamp, str) or not isinstance(message, str):
                fail(f"malformed user message in {rollout_path} on line {line_number}")
            if (CODEX_DELEGATION_PATTERN.match(message) or opening_of(message) in SENT_BY_AGENTS_THROUGH_T3
                    or message.lstrip().startswith(AGENT_WRITTEN_OPENINGS)):
                continue
            user_messages.append((timestamp, message))

        if not found_matching_session_metadata:
            fail(f"rollout does not identify itself as task {thread_id}: {rollout_path}")

    if not user_messages:
        if not required:
            return None
        fail(f"task {thread_id} has no human messages")

    return {
        "thread_id": thread_id,
        "user_messages": user_messages,
    }


arguments = parse_arguments()
codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).resolve()
explicit_thread_ids = [normalize_thread_id(value) for value in arguments.thread_ids]
if len(explicit_thread_ids) != len(set(explicit_thread_ids)):
    fail("duplicate Codex task ID")
project_thread_ids = (
    human_project_thread_ids(codex_home, arguments.project_root) if arguments.project_root else []
)
thread_ids = project_thread_ids + [thread_id for thread_id in explicit_thread_ids if thread_id not in project_thread_ids]

output_path = arguments.output.resolve()
thread_records = [
    record for record in (
        extract_thread(codex_home, thread_id, required=thread_id in explicit_thread_ids) for thread_id in thread_ids
    ) if record is not None
]

bundle_sections = [
    "User messages from Codex rollouts, for review.",
    "Mechanically extracted in stored order. Assistant messages, Codex delegation briefs and messages T3 Code records as sent by an agent are excluded. These filters are not proof that every message left is the human's.",
]
if THREADS_NOT_READ:
    bundle_sections.append(f"Not read, so this is not all of the steering: {len(THREADS_NOT_READ)} task(s).")
    bundle_sections.extend(f"- {thread_id}: {reason}" for thread_id, reason in THREADS_NOT_READ.items())
bundle_sections.append("")

for thread_index, thread_record in enumerate(thread_records, start=1):
    thread_id = thread_record["thread_id"]
    bundle_sections.extend(
        [
            f"<<< TASK {thread_index} | {thread_id} >>>",
            "",
        ]
    )

    for message_index, (timestamp, message) in enumerate(thread_record["user_messages"], start=1):
        bundle_sections.extend(
            [
                f"<<< USER MESSAGE {thread_index}.{message_index} | {timestamp} >>>",
                message,
                f"<<< END USER MESSAGE {thread_index}.{message_index} >>>",
                "",
            ]
        )

    bundle_sections.extend([f"<<< END TASK {thread_index} >>>", ""])

transcript = "\n".join(bundle_sections).encode("utf-8")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_bytes(transcript)
if output_path.read_bytes() != transcript:
    fail("written human-message transcript differs from generated transcript")

print(f"human_messages={output_path}")
if THREADS_NOT_READ:
    print(f"not_read={len(THREADS_NOT_READ)} (listed at the top of the file)")
