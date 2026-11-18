# jjpstack

<!-- PLACEHOLDER: Josh dictates this part. What jjpstack is, why it exists, how he works with agents. -->

## What's in it

- `skills/`: agent skills for Claude Code and Codex.
  - `better` and `even-better`: deeper work, the way a top professional would do it.
  - `working-with-other-agents`: pass on the user's own words, treat other models as colleagues, review cold.
  - `prompting-models`: give models the goal, the context and how to check the result, not orders.
  - `picking-models`: which model to use for what, and when to mix model families.
  - `raw-steering`: work from what the user actually said, read in full, with scripts that read each harness's records.
  - `writing`: plain English, to Gowers' *The Complete Plain Words*.
  - `engineering`: engineering principles. Runs only when invoked as `/engineering`.
- `t3/`: setup for [T3 Code](https://github.com/pingdotgg/t3code).
  - `t3-code-overrides.md`: an extra system prompt for every Claude and Codex thread.
  - `t3-codex.sh` and `t3-settings.nix`: how it reaches Codex, and T3's defaults. They're Nix from a nix-darwin setup, so adapt them to yours.
- `claude-code/`: Claude Code hooks and the settings that wire them in.
  - `cut_output_reminder.py`: after a shell command that cut its own output (`head`, `tail`, `grep -v` and the like), tells the agent it read a sample.
  - `after_compaction.py`: after a compaction, writes out every message the user sent in the session and has Claude read them before carrying on.

## Install

Copy the skills you want into `~/.claude/skills/` (Claude Code) or `~/.agents/skills/` (Codex). Copy the hooks into `~/.claude/hooks/` and merge `claude-code/settings.json` into `~/.claude/settings.json`. Give Claude the T3 prompt with `--append-system-prompt-file`, and Codex with `t3-codex.sh`.

The skills are written for one person, Josh, and name him. Change that to you.

This is a snapshot. The working copies live in a private repo and change often.
