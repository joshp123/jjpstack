# jjpstack

There are many skill packs. This one is mine.

I've been building with agents for about a year. I was one of the earliest maintainers of [OpenClaw](https://github.com/openclaw/openclaw) ([#39](https://github.com/openclaw/openclaw/pull/39), [#40](https://github.com/openclaw/openclaw/pull/40)), and now I build open source personal agent tooling for myself: [OpenTrawl](https://github.com/opentrawl/opentrawl). I currently use the [T3 Code](https://github.com/pingdotgg/t3code) harness to build in.

These are the skills I found essential in my daily work with agents. Most of them paper over deficiencies in the models: things they do poorly, and with these skills they actually do better. They're simply my opinions on building with agents over the last year.

## Skills

- **better** asks for deeper work, the way a top professional would do it. Inspired by [Felix Rieseberg's tweet](https://x.com/felixrieseberg/status/2110023283169247623). It reaches deep into the model's training data to get it to do the things it already knows but didn't tell you the first time. **even-better** pushes harder.
- **working-with-other-agents**, **prompting-models** and **picking-models**: the labs publish guides on how to prompt their models, but clearly haven't trained the models to prompt models. Models yell at their sub-agents and give them overly prescriptive tasks, when the guides say to give a goal, your intent and how to verify the work is done. Reference these in your AGENTS.md and the models prompt how they're supposed to.
- **raw-steering** fixes the Claude problem where the model is lazy and only samples your words, instead of reading them in full or passing them in full to other agents.
- **writing** is my latest iteration of getting models to write with minimal slop. It's not great, it's not terrible. You need to invoke it multiple times for the models to actually remember it.
- **engineering** is my opinionated take on engineering. It might not be yours, but it's mine.

## Harness

- **T3 overrides** fix how Claude and Codex (especially Claude) take your attention away. They tell Claude when to shut the fuck up, when to ask you questions and when to actually demand your attention. The idea is it demands less of it.
- **Compaction hook** for Claude Code. Claude's compaction gets many things wrong, so this forces it to read in your entire steering all over again. Not very token efficient, but much better than it having the wrong idea of what you said.
- **Cut-output hook** for Claude Code tells Claude when it only read a sample of a command's output.

## Install

Paste this to your agent:

```
Install jjpstack from https://github.com/joshp123/jjpstack. Read the README and every file, then set up the skills, the Claude Code hooks and, if I use T3 Code, the T3 overrides, for my machine and harnesses. The files are written for Josh: change his name to mine. Show me what you'll change in my existing setup before you change it.
```

This is a snapshot: my working copies live in a private repo and change often.

## Talk to me

If you like it, talk to me on X at [@jjpcodes](https://x.com/jjpcodes). If you don't like it, you can yell at me, I guess. If you have an idea to make it better, you can also yell at me.
