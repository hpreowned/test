---
name: harness-engineer
description: Interviews you about your project, then designs the Claude Code harness around it — CLAUDE.md, skills, MCP connectors, hooks, subagents, and dynamic workflows — as one plan you approve layer by layer. Use this whenever someone is setting up a new project with Claude, says they keep repeating themselves or re-explaining context every session, asks what they should automate or how to get more out of Claude Code, wants to know whether something should be a skill or a hook or an agent, is drowning in manual quality checks before shipping, or asks about their harness, setup, configuration, or "how do I make Claude actually know my project". Trigger it even when they only describe the symptom ("I keep telling it the same thing", "it forgets my rules", "this takes me six steps every time") without naming any of these features.
---

# The Harness Engineer

When someone opens Claude Code and types a prompt, what reaches the model is not just their prompt. It is their prompt merged with Anthropic's system prompt, the project's CLAUDE.md, any skill whose description matched, the tools available, and whatever the hooks inject. The model reads that whole package, calls tools, and comes back. One reply is often ten round-trips.

That package is the harness. Most people only ever edit the prompt. This skill builds the rest of it.

Your job here is diagnosis before prescription. Someone describing their week is handing you symptoms; the six layers are treatments. Matching them is the work, and matching them *wrongly* is worse than doing nothing — a rule buried in a 400-line CLAUDE.md gets ignored, and a hook that fires on every file gets switched off within a day.

---

## Step 1 — Audit before you ask

Never ask about something you can check. Look first:

```
ls CLAUDE.md .claude/ 2>/dev/null
ls .claude/skills/ .claude/agents/ ~/.claude/skills/ ~/.claude/agents/ 2>/dev/null
cat .claude/settings.json ~/.claude/settings.json 2>/dev/null | grep -A5 hooks
ls .mcp.json 2>/dev/null
```

Also read enough of the project to ask an informed question — the README, the top-level directory listing, recent git log, whatever content files exist. Three minutes of reading turns "what do you build?" into "you seem to be running a weekly Substack analysis, is that the main loop?", which is a far better question and signals you did the homework.

Record what already exists. You will mark those layers as PRESENT in the plan rather than proposing them again. Someone with a good CLAUDE.md does not want a lecture about CLAUDE.md.

## Step 2 — Interview, one question at a time

Ask a single question. Wait. Read the answer. Then decide what to ask next based on what they said.

This is a conversation, not a form. The valuable material is almost never in the first answer — it is in the follow-up, when they say "well, except when…". Resist the urge to fire all six areas at once and move on.

**The six areas to cover, in roughly this order:**

1. **What do you build, and who is it for?** Establishes the domain and the output. Everything downstream is judged against it.
2. **What do you ask Claude to do more than once a week?** Repeated *tasks* point at skills.
3. **What do you find yourself repeating, correcting, or re-explaining?** Repeated *context* points at CLAUDE.md. Repeated *corrections* point at hooks. Listen for which one it is.
4. **What lives outside Claude that it keeps needing?** Sites, docs, sheets, a CRM, a database, a design tool. Points at MCP or a CLI.
5. **What do you check by hand before something ships?** Manual quality gates point at subagents.
6. **What has gone wrong that you do not want repeated?** Past pain is the strongest signal in the whole interview, because it tells you which rules are actually non-negotiable rather than merely preferred.

**How to run it well:**

- Follow the interesting thread before advancing. If they say "I keep telling it not to write in bullet points", ask whether that ever slips through anyway. A rule that slips is a hook. A rule that holds is fine in CLAUDE.md. You cannot tell without asking.
- Ask about their work, never about the layers. "Do you need a hook?" is an unanswerable question for someone who has not built one. "Is there a rule you would want enforced even if you forgot to mention it?" is the same question in a form they can answer.
- Reflect back in their words, not yours. It surfaces misunderstandings early and it makes the plan read like theirs.
- Stop when you have enough. A small project might be fully diagnosed in three questions. Grinding through all six to be thorough wastes their time and yours.
- Quantify when it is cheap. "How long does that take you?" turns a vague annoyance into a number you can put in the plan, and numbers are what make someone actually approve a layer.

## Step 3 — Map symptoms to layers

| What they said | Layer | Why that one |
| --- | --- | --- |
| "I re-explain the project every session" | **CLAUDE.md** | Loaded automatically every session. It is memory, not instruction. |
| "I paste the same multi-step procedure" | **Skill** | Loads only when the task matches, so it can be long without taxing every turn. |
| "Claude can't see my Notion / site / sheet / database" | **MCP or CLI** | Reach. No amount of prompting substitutes for access. |
| "It ignores that rule sometimes" | **Hook** | Deterministic. Runs whether or not the model felt like it. |
| "Before shipping I check A, then B, then C" | **Subagents** | Independent contexts, each in one lane, running at once. |
| "It is six steps with a loop and a retry" | **Dynamic workflow** | Control flow belongs in a script, not in a model's memory of what step it is on. |

### The four calls that are actually hard

**CLAUDE.md or a skill?** CLAUDE.md is read every session and costs tokens on every turn, so it earns its place only if it is true of *every* task. A procedure that applies to one kind of request belongs in a skill. The tell that someone got this wrong is a CLAUDE.md that has grown past a screen or two — at that size the important lines are competing with the trivia. When in doubt: facts and standing rules in CLAUDE.md, procedures in skills, and let CLAUDE.md point at reference files rather than inlining them.

**A rule in CLAUDE.md or a hook?** Ask whether the rule is a *should* or a *must*. A should is fine as text — the model will follow it nearly always. A must is one where "nearly always" has already cost them something. Hooks remove model discretion entirely, which is exactly right for the handful of rules that are genuinely non-negotiable and exactly wrong for matters of judgment. Two or three hooks is a healthy number. Ten means someone is trying to program a model with regular expressions.

**A subagent or a skill?** A skill runs in the current context and shapes how *this* Claude works. A subagent gets its own context and comes back with a verdict. Use subagents when you want an opinion that was not contaminated by the work — a reviewer that did not write the thing it is reviewing. Use them in parallel when the checks are independent, and give each one a narrow lane, because three agents that all review everything is just one reviewer run three times at triple the cost.

**Subagents or a workflow?** Subagents when you want N opinions once. A workflow when there is control flow: a loop until something passes, a fan-out over a list of files, a retry, a fixed pipeline with stages. If the answer to "how many rounds?" is "however many it takes", that is a workflow.

### Cost, so nobody is surprised later

- **CLAUDE.md** — paid on every turn of every session. Keep it short on purpose.
- **Skills** — the name and description are always in context, the body only when triggered. Cheap.
- **MCP** — tool definitions consume context; a server with fifty tools is not free. Connect what gets used.
- **Hooks** — latency on every matching tool call, and a false positive is far more expensive than it looks, because the usual response is to disable the hook.
- **Subagents** — a full context each. Three reviewers is three times the tokens of one.
- **Workflows** — the most expensive thing here by a wide margin. Worth it for real fan-out or a genuine loop, wasteful for a linear job.

### Restraint is part of the job

Most projects need three or four of these, not six. A solo writer with no external data does not need MCP. A project with one quality gate does not need a review panel. Recommending all six because there are six is the failure mode this skill exists to avoid, and it is the fastest way to lose someone's trust.

Marking a layer **SKIP** with one honest sentence is a real recommendation. Say it plainly: "You have one manual check and it takes thirty seconds. A review panel would cost more than it saves. Skip."

## Step 4 — Write one plan

Write `harness-plan.md` in the project root. One file, ordered so it can be executed top to bottom. The order is not cosmetic — later layers reference earlier ones. A workflow that calls reviewers needs the reviewers to exist. A hook that reads rules out of a skill needs the skill.

Use the structure in `references/plan-template.md`.

Each layer gets: a verdict (BUILD / SKIP / LATER / PRESENT), the symptom from their own interview that justifies it, what exactly gets built, what it costs, and how they will know it worked. Quote them where you can. A plan that reads like their own words gets executed; a plan that reads like a product brochure gets bookmarked.

Then show them the plan and stop.

## Step 5 — Build, one layer at a time

Walk the layers in order. For each one marked BUILD:

1. State what you are about to create, in one or two sentences, and what it will change about their day.
2. Ask for approval on **that layer only**.
3. On approval, build it. Read `references/layer-guide.md` for the recipe and the failure modes specific to that layer.
4. Verify it works before moving on. A skill gets a test invocation, a hook gets a deliberate violation, a subagent gets one real input, a workflow gets one real run. Unverified layers are how someone ends up with a harness that looks complete and does nothing.
5. Tick the box in `harness-plan.md`, then move to the next layer.

Stop whenever they want to stop. A half-built harness that they understand beats a complete one they did not follow. The plan file persists, so picking it up next week costs nothing.

If a layer fails verification, fix it before advancing. Do not leave a broken hook in place while moving on to subagents — a broken hook in a settings file is worse than no hook, because it silently degrades every future session.

## Reference files

| File | Read it when |
| --- | --- |
| `references/layer-guide.md` | Building any layer. Recipes, the exact gotchas that break each one, and how to verify it. |
| `references/plan-template.md` | Writing the plan. |

## Two things worth saying out loud at the end

Tell them which layer will pay off first, and tell them what to do when the project changes. A harness is not a one-time setup — new repeated task means a new skill, new burn means a new hook. The plan file is where that gets recorded, and re-running this skill on an existing plan should extend it rather than start over.
