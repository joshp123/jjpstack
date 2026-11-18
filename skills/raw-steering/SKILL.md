---
name: raw-steering
description: Work from what Josh actually said, all of it, instead of an agent's summary of it. Use before starting or resuming work that depends on what he wants, after a compaction, when taking over a thread or project, before briefing another agent, and whenever all you have of his intent is a summary, memory or handoff.
---

# Raw steering

The goal is to work from what Josh actually said: every message of his on the task, read start to finish, each with the agent line it answers. A summary, memory, handoff or "Josh wants X" line is someone's reading of him, and current models misread him often: in an audit of 41 compactions, 76% lost or twisted his intent. His meaning often turns in the last clause, and a later message overrides an earlier one only on the point it addresses.

Harnesses store some agent text exactly as they store his, so reading a transcript by eye gets authorship wrong. The opening prompt of a T3 child thread is the parent agent's, agents write into T3 threads and Grok chats in his account, and in July 2026 agents typed into terminals as him. Where a record can't show who wrote something, the author is unknown. These scripts read each harness's own records, from this skill's folder:

```sh
python3 -I -B scripts/josh_words.py t3 ['ID OR TITLE WORDS'] [--both]   # T3 threads, any provider; no argument lists them
python3 -I -B scripts/josh_words.py claude SESSION_ID_OR_PATH           # a Claude Code session
python3 -I -B scripts/conversation.py SESSION_ID                        # that session, both sides
python3 -I -B scripts/extract_human_transcript.py --output FILE [--project-root REPO] [THREAD_ID ...]   # Codex
python3 -I -B scripts/josh_words.py grok ['CHAT NAME']                  # Grok Bot; no argument lists the chats
```

Use `--both` or `conversation.py` when his replies are short, because a plain reply is stored without the message it answers. The scripts read the machine they run on. After a compaction, Claude Code's hook also writes his messages from the session to a file and says where. How each harness records authorship, and what the scripts can't tell, is in [reading-sessions.md](references/reading-sessions.md); when output looks wrong, check the store, then fix the script and that file.
