# jjpstack

There are many skill packs. This one is mine.

I've been building with agents for about a year. I was one of the earliest maintainers of [OpenClaw](https://github.com/openclaw/openclaw) ([#39](https://github.com/openclaw/openclaw/pull/39) and [#40](https://github.com/openclaw/openclaw/pull/40)), and now I build open-source personal agent tooling for myself, currently in the [T3 Code](https://github.com/pingdotgg/t3code) harness. These are the skills and harness changes I use to make that happen, and they're simply my opinions.

Most of them paper over deficiencies in the models: things the models do poorly, and do better with these skills.

## Skills

**better** and **even-better.** `better` is inspired by an Anthropic tweet that asks for deeper work, the way a top professional would do it. It reaches deep into the model's training data to get it to do the things it already knows but didn't tell you the first time, for whatever reason. `even-better` pushes it harder.

**working-with-other-agents, prompting-models and picking-models.** The models share a failure mode. The labs publish guides on how to prompt their models, but they clearly haven't trained the models to prompt models. You can see it when models talk to sub-agents: they yell at them and give them overly prescriptive tasks. The labs' guides say to give a model an overall goal, your intent, and how to verify the work is done. Models prompting sub-agents do the exact opposite. Reference these skills in your AGENTS.md and the models prompt the way they're supposed to, and it works much better. `picking-models` says which model to use for what, with my views and Theo's.

**raw-steering** fixes the Claude problem where the model is lazy and samples your words, instead of reading them in full or passing them in full to other agents.

**writing** is my latest attempt at getting models to write with minimal slop. It's not great and it's not terrible: you need to invoke it several times before the models remember it.

**engineering** is my opinionated take on engineering. It might not be yours, but it's mine.

## Harness changes

**The T3 overrides** fix deficiencies in Claude and Codex, especially in how Claude takes your attention away. They give you your attention back by telling Claude when to shut the fuck up, when to ask you questions, and when to actually demand your attention. The idea is that it demands less of it.

**The compaction hook** for Claude Code makes sure Claude still understands what you said. Claude's compaction gets many things wrong, so after a compaction the hook makes it read all your messages again. That isn't very token-efficient, but it's much better than Claude acting on something the summary says you said when you didn't.

**The cut-output hook** reminds Claude, after a shell command that cut its own output (`head`, `tail`, `grep -v` and the like), that it has only read a sample.

## Install

- Skills: copy the folders you want from `skills/` into `~/.claude/skills/` (Claude Code) or `~/.agents/skills/` (Codex).
- Claude Code hooks: copy `claude-code/hooks/` into `~/.claude/hooks/` and merge `claude-code/settings.json` into `~/.claude/settings.json`.
- T3: give Claude `t3/t3-code-overrides.md` with `--append-system-prompt-file`, and Codex with `t3/t3-codex.sh`. `t3-settings.nix` is from my nix-darwin setup, so adapt it to yours.

The skills are written for me and name me; change that to you. This is a snapshot: my working copies live in a private repo and change often.

## Talk to me

If you like this, talk to me on X, [@jjpcodes](https://x.com/jjpcodes). If you don't like it, don't yell at me. If you have a good idea to make it better, tell me and I might think about it.
