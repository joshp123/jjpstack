---
name: picking-models
description: Which model to use, and how to mix models from different labs: scores for current Claude, OpenAI and Google models on intelligence, taste, diligence and cost, from Josh's and Theo Browne's views, with how to route work and when to bring in another model family. Use before starting a sub-agent, delegate or review, and whenever choosing a model or effort setting.
---

# Picking models

Scores out of 10, higher is better. One number where Josh and Theo agree; both where they differ.

- **Intelligence:** how hard a problem you can hand the model unsupervised.
- **Taste:** UI and UX, code quality, API design and copy.
- **Diligence:** whether it reads and checks everything, or samples and assumes.
- **Cost:** what it actually costs to use on subscriptions.

| Model | Intelligence | Taste | Diligence | Cost |
| --- | --- | --- | --- | --- |
| Fable 5.2 | 10 | 9 | 5 | 2 |
| Opus 5.5 (high) | 9 | 8 | Theo 9 / Josh 6 | 9 |
| GPT-6.2 Astra | 7 | 3 | 10 | 4 |
| GPT-6.1 Sol | 7 | 3 | 9 | 8 |
| GPT-6.1 Terra | Theo 4 / Josh 6 | 3 | 8 | 8 |
| Sonnet 5.5 | 6 | 6 | 5 | 5 |
| Haiku 5.5 | 3 | 4 | 4 | 10 |
| GPT-6 Luna | 3 | 3 | 7 | 10 |
| Gemini 4 Neon | 9 | 8 | 6 | 7 |
| Gemini 4 Carbon | 5 | 3 | 2 | 3 |
| Gemini 4 Argon | 4 | 3 | 1 | 3 |

## Traits by lab

- **Claude models** understand intent and have taste, but are lazy readers: they sample output and conversations, then act as if they read it all. They also over-build when they accept every suggestion.
- **OpenAI models** are turbo-autistic: exhaustively literal and precise, they read everything and miss nothing. They are poor at judgement, orchestration, writing and UI, and without a precise spec they drift into autism soup.
- **Google** made a break with Gemini 4 Neon. Argon and Carbon hallucinate too often for agentic work; Neon is coherent on long runs, writes the most readable prose, and rivals Opus for code. It still makes some things up when only analysing, and is weak at 3D.

## How to apply

- Gemini 4 Neon is Josh's daily driver: it is really smart. Opus 5.5 on high is still a great workhorse. Opus medium is noticeably lazier; low and max are worse still.
- Fable for UI and design work, and to lead the hardest problems, especially agentic development. Opus can do the building under it. Handing implementation to Astra or Sol is worth trying as an experiment.
- OpenAI models for work where completeness matters more than judgement: review, audit, verification, legal reading, deep debugging.
- When a Claude model must read everything, force full reads, or give the job to an OpenAI model.
- Never put an OpenAI model on UI or user-facing copy.
- Have a Claude model explain OpenAI output to a person.
- Gemini 4 Neon for copy and long-horizon engineering, and as a third family in reviews. Gemini 4 Argon and Carbon never write code. Haiku and Luna do bulk work over data, never code.

## Mixing families

Claude brings writing, design and judgement; GPT brings autistic checking. Each catches what the other misses, so bring the other family in where it changes the outcome. Don't do it at every step: extra agents cost time and tokens, and a review is no substitute for checking your own work first.

- Whether work merits a cross-family review is Josh's call, because only he knows how much it matters to him. Ask him, with your view. It usually does for work with real-world impact (a deploy, anything sent to another person, money, legal matters, security, accounts) and for technical designs that need an adult in the room.
- Brief the reviewer with Josh's words and the work, not your framing, and tell it to advocate for him. Treat its findings as input, not orders: Astra is strict but poor at judgement, and will over-build or hedge if followed blindly.
- When working mainly with an OpenAI model, bring in a Claude model now and then to judge, write and keep the work grounded in the real world, so it doesn't drown in autism soup.

For how to brief the other model, read the working-with-other-agents skill.

## Where Josh and Theo differ

- **Opus diligence:** Theo sees a careful model that checks everything. Josh finds Claude models sample and skim unless hooks force full reads.
- **Fable's prose:** Theo rates it the most readable. Josh finds Opus writes better.
- **Terra:** Theo found no use for it. Josh rates 6.1 Terra well for computer use.
