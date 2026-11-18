---
name: prompting-models
description: Write instructions that current models follow well, so other agents and future sessions succeed with their own judgement. Use whenever you write a prompt, brief or delegate message, a message to another agent, a skill, CLAUDE.md or AGENTS.md text, or a system prompt.
---

# Prompting models

The goal is that the model reading your prompt knows what success is and why, has the context only you can give it, and uses its own judgement for everything else.

Your instincts for writing prompts are out of date, and that is why models keep prompting each other badly. Most of the prompting advice and examples you learned from were written for weaker models, which needed rules, capitals, step-by-step recipes, worked examples and reminders to think. Current models (Claude Fable 5.2 and Opus 5.5, GPT-6.2 Astra and Sol, GPT-6.1 Terra) plan, check and persist on their own, and they follow instructions closely and literally, so those habits now over-constrain them. Anthropic removed about 80% of Claude Code's own system prompt with no measurable loss, and OpenAI warns that skills written as itineraries or recipes now hinder results. The pull is strongest when you are unsure, because adding a rule feels like care.

A good prompt holds three things. The goal: what the whole piece of work is for, and how this part feeds it. The finish line: what done looks like, and how the reader can check it. And the context the reader can't get anywhere else: the user's own words, their taste and quality bar, how their environment works, and the reason behind each real constraint. Give more of that context than seems necessary, and nothing else.

Everything else costs more than it gives. A method where a goal belongs replaces the reader's plan, which is usually better than yours. A rule without its reason, a list of prohibitions or words in capitals make the reader rigid and cautious, and can steer it towards the failure they name. An example narrows the reader to copying its length, tone and shape. A story about a past failure stands in for the principle it taught. Text the reader already knows, or would act on anyway, only gives it noise to reconcile. How hard to think is for the effort setting, not the prompt.

These models apply a rule as it is written, Claude Fable 5.2 most of all. A caution written for one case then holds back routine work everywhere, and a general line telling the reader to act more freely changes nothing. So a limit carries its scope, its reason and its exception in the same sentence: which actions it covers, why, and what counts as a go-ahead. Cautions also pile up in memory, notes and instruction files, and models keep obeying them after the reason has gone: delete a caution once its reason no longer holds. A standing instruction to delegate does the same to cost, because agents then start sub-agents the task doesn't need.

Length is not the measure. Every word should change what the reader understands or does: cutting context makes a prompt worse, and so does padding it. "Every token earns its place" is the test; "make it short" is not. In a skill, keep what every use needs in the main file and point to the rest, so it loads only when it's needed.

Before you send or save a prompt, read it as the model that will receive it. Could it succeed with only this? Does it know why? Is there anything in it the model would do anyway? When the prompt is a brief for another agent, the working-with-other-agents skill covers whose words go in and who instructs.

These lessons fit the models of November 2026. They come from the vendors' own guides: Anthropic's [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), [Prompting Claude Fable 5.2](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2) and [Prompting Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5), and OpenAI's [Using GPT-6.2](https://developers.openai.com/api/docs/guides/latest-model). When a new model ships, read its vendor's guide and update this skill.
