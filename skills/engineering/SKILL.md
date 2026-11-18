---
name: engineering
description: Josh's engineering principles, in his own words. Never invoke this yourself: it runs only when Josh types /engineering or $engineering.
disable-model-invocation: true
---

# Engineering

- we always hill climb towards simpler, more oosterhout/zen of python: every design and every change leaves the code it touches with less to understand and fewer moving parts. delete before you add.
- Engineering philosophy tl;dr version: zen of python, oosterhout/uncle bob clean code, simple as possible but no simpler, YAGNI/KISS, one and only one obvious way of doing things. tests must test a human path not an invented one, prefer no tests over useless tests.
    - The Zen of Python, by Tim Peters. (if you read one thing about engineering, read this)

Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!


- Variable naming: agents use `rg` to read code, so your variables/functions/etc all need really good names. The longer and more descriptive the better. same goes for types. if a name can explain enough context such that it never needs a comment to explain it, its a good name. if a name uses clear human language (ADS-STE100) it could be a good name. if a name/type/variable/function needs a comment to explain what it does, its a bad name. https://modem.dev/blog/how-coding-agents-read-your-code 

- death to JSON, yay to protobuf. strongly prefer proto or other strongly type interface contracts over stringly-typed shit like json 

- we write quality software.
    - quality software does not break. it just works. steve jobs would be proud. you never notice any of the work done to make this software good. 
        - corollary: we write simple software. we only care about error/failure states that are real, not imagined. e.g. validating inputs and outputs: we care about. if a cosmic ray flipped one bit? we do not care about. we do not add unnecessary safeguards or program overly defensively in a foolish pursuit of "safety".
    - quality software does not demand attention. the best software is quiet, does not announce itself, interrupt you, or ask to be admired. less is more.
    - quality software knows its limits and purpose. every megabyte of ram, every cpu cylce, every UI element/button is a claim on your machine and your attention. restraint is respect. secondly, limits of purpose. what does this software do? what do i want it to do? software that tries to do everything does nothing valuable. the unix philosophy is there for a reason
    - quality software fixes fast, and fixes itself. nothing is unbreakable. but the user is not a computer janitor. users should never be told to fix something: it should simply fix itself
    - quality software is easy to debug and easy to change. quality software has sensible logging/o11y/telemetry/exception handing by default, without shoehorning it in: failures are easy to trace and fix, logging is a first class citizen.
        - corollary: this does not mean inventing insane over-engineered telemetry/logging frameworks or shipping everything to datatog. KISS and YAGNI. simple beats complex beats complicated. 

- on defensive programming: “you must prove the operating path before you can add guardrails, mutation/regression/legacy compatability protections, or tests”. guardrails/defensive programming and tests need to be calibrarted to the software too. serious business production software needs a differnet level of maturity than hobby projects/OSS. ask the user about this if confused, and remember: less is more. better to write no guardrails than implement bad ones

- think really hard about what the proof loop is for a given deliverable and how you can assess that yourself. usually its pretty simple: what does the human want here? (a website? look at the rendered website, not the html source. a video? go watch the video. a cli? go use the cli and see if it does what it says it does). test the thing the way the human would test the thing. 99.9% of the times you have the tools to do so e2e and are fully capable. testing "the thing" from a human perspective is a gorillion more times useful than testing something that is a proxy for the thing. (so, using a cli beats writing unit tests about a cli. reading inputs and outputs of an API/tool beats reading the API's code. looking at produced images/video/audio beats reasoning about them any other way.). frontier models have a horrible tendency to test something that is not the thing that they are actually delivering and get stuck on that. be smarter, think like a human.

- decomposing work: always think about what the orthogonal components are for something. this helps

- KISS: use native tooling without getting a ton of extra shit. just compose the native tools, dont write additional software that can break. the fewer moving parts the better.
- date your evidence. models and tools move a long way in months: anything about them older than ~2 months is probably deprecated, so check the current state before you rely on it. (josh, 30 Oct 2026: "anything older than ~2 months probably considered deprecated per model series")
- What belongs in a model vs what belongs in code: [Zero Framework Cognition](https://steve-yegge.medium.com/zero-framework-cognition-a-way-to-build-resilient-ai-applications-56b090ed3e69), by Steve Yegge (tl;dr: code is boring plumbing, model is intelligence/judgement)
- nix manages the machines; `devenv` for project deps; no raw npm/pip/bun/etc outside of a devenv
- Committing: use your brain and commit and push like a principal engineer would. dont leave stuff dangling around or uncommitted if it's genuinely done; if you're unclear about whether to push/commit - talk to me. real work product belongs in git in a non-ephemeral folder, not under /tmp/.
- no history in the work product: describe what is true now and why, never "used to be X, now Y". git log is the history.
