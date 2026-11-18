# How each harness records who typed what

Checked against the stores on 30 October 2026. Formats change without notice, so when a reader's output looks wrong, go to the store, then fix the script and this file.

## Claude Code

`~/.claude/projects/<folder>/<session id>.jsonl`, one JSON event per line.

- His turns are `type: "user"` events, with `message.content` as a string or as `text` blocks. Tool results are `user` events too, as `tool_result` blocks.
- Not his: events with `isMeta`, `isCompactSummary` or `isSidechain` (a sub-agent), or a present `origin.kind` other than `human`. Many turns have no `origin`, and that proves nothing.
- A message he sends while the agent is working is not a `user` event. It is `type: "attachment"`, with `attachment.type: "queued_command"`, `attachment.origin.kind: "human"` and the text in `attachment.prompt`.
- Inside his turns, `<system-reminder>` blocks are the harness's. Turns opening with `<task-notification>`, `<local-command-stdout>`, `<side-sessions-event>`, `[Request interrupted by user`, `This session is being continued from a previous conversation` or `Delegated task node:` are not his.

## T3 Code

Sessions T3 drives carry no `origin`, so their transcripts can't show who sent what. An agent's opening brief to a child thread looks like his turn. T3's own database can: `~/.t3/userdata/statev2.sqlite`, table `orchestration_v2_projection_messages`, whose `payload_json` holds `createdBy`, `creationSource` and `text`.

- `createdBy: "user"` with `creationSource` of `web` or `mobile` is what he typed.
- `createdBy: "agent"` is an agent. `server` rows with `createdBy: "user"` sit in `import:` threads and are copies of older sessions.
- `josh_words.py t3` reads this table directly, so it works for threads run by any provider and needs no transcript. `--both` adds the agents' messages from the same table, and marks any message T3 didn't record an author for.
- On an `import:` thread, `josh_words.py t3` reads the original Claude Code session instead, if its transcript is on this machine, and otherwise says that authorship can't be told.
- `josh_words.py claude` drops a transcript turn when its first 300 characters match an agent's row. Without the database it drops nothing, so agents' briefs print as his.
- When he comments on a quoted passage, the message is a link: `[Assistant quote](t3-citation://...?text=...&comment=...)`. The passage and his comment are URL-encoded in the query.

## Codex

`~/.codex/sessions/**/*<thread id>.jsonl`, indexed by `threads` in `~/.codex/state_5.sqlite`. Both `~/.codex/archived_sessions/` and `sessions/` can hold compressed `.jsonl.zst` rollouts as well as plain ones. The script can't read the compressed ones (this Mac has no `zstd`). A project export lists every thread it skipped at the top of its output, so a partial export can't pass for the whole, and a thread asked for by id stops with the reason.

- Typed turns are `event_msg` records with `payload.type: "user_message"`, or `item_completed` with a `UserMessage` item.
- `session_meta` names the thread. `--project-root` skips threads whose `source` is `exec` or holds `subagent`.
- Rollouts don't say who sent a message. The script drops `<codex_delegation` wrappers, text opening `Task:` or `[Agent-to-agent message`, and matches against T3's agent rows. These are filters, not proof: Josh could open a message with `Task:`, and an agent's text can pass all of them.

## Grok Bot

`~/Library/Application Support/Grok Bot/sand-client-persistence/*.blob`, or the folder in `GROK_STORE`. Each is JSON with a `value`, and each file name is the slice name in unpadded base32. The roster slice ends `.roster.last-roster`; each chat is `.transcript.replicas.<bot id>`, a local copy of about the last 200 entries.

- Chat `entries` have `kind`, `role`, `content` and `timestampMs`.
- `fromAgent` and `toAgent` mark messages between bots, and `kind: "send-message"` is a bot writing to him.
- Anything typed in his account is `role: "user"`, agents included. Nothing marks it except the agents' own habit of saying "not Josh" near the start, which the reader looks for.
- A post he tagged @bot on X arrives wrapped in text opening `You were invoked from a public X @bot mention`.

## What no store shows

In July 2026 agents drove terminal sessions, and what they typed was logged as his. Treat July "user" messages with care: where a record can't show the author, the author is unknown, not Josh.
