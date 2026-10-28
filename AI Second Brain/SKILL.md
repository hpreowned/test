---
name: second-brain
description: Build an autonomous AI second brain — pull your own data out of Claude.ai and Claude Code, process it into clean notes, compile it into a self-growing wiki (Karpathy's LLM-Wiki pattern), then run agents that read the wiki + raw data and write you fresh analysis on a schedule. A reusable recipe, tool-agnostic, for any domain. Triggers — "second brain", "build a brain from my chats", "Karpathy wiki", "agent that analyzes my data", "process my Claude conversations".
---

# Build Your Own AI Second Brain

A second brain that **thinks for you while you sleep**. Not a notes app you query — a system that pulls your own history, compiles it into a living wiki, and runs agents that surface insights you'd never find by scrolling.

This is the reusable recipe. It works for any goal (a newsletter, a business, research, your life). Swap "articles" for whatever you produce.

---

## How an agent runs this skill (start here)

If you are the AI reading this for a user, do NOT dump the whole recipe at them. Build it *with* them, step by step. Run this loop:

**Step 0 — Interview (never hard-code paths).** Ask the user:
1. Where is their Claude Code history? (default `~/.claude/projects/` — confirm it exists)
2. Did they export their claude.ai data? (Settings → Privacy → Export data → emailed zip). Get the zip path, or tell them to export and come back.
3. **Their OWN published/produced work** — what they make, not just their chats. Newsletter posts, blog articles, notes, client deliverables, code, designs… Get the folder/export. This is the heart of the brain: their conversations show *how they think*, but their work + its results show *what actually lands*.
4. **Their OUTCOME numbers** — for that work: what got likes, paid, shipped, earned, converted. (A CSV / analytics export.) Without outcomes the wiki only says "here's a topic"; with them it says "this topic earned X, that one earned nothing." This is the edge.
5. What is their GOAL / domain? (newsletter, business, research, life) — this names the wiki entities later.
6. **What CONNECTIONS / lenses do they want?** These are the agents that will read the finished wiki — one per angle they care about. Examples: *what already worked* (mine past work + outcomes), *what to build next* (surface unfinished builds), *coach me* (read their journal + profile), *what to write next* (study their best pieces). They pick 2-5; each becomes a scheduled agent writing to its own journal folder.
7. **What must be EXCLUDED?** (a partner's chats, clients, private topics). Get explicit keywords. Mandatory before any processing.
8. Where is the Obsidian vault? (create one if none) — all output goes here.
9. Do they have an always-on machine + a scheduler (Hermes/OpenClaw/cron)? If not, the brain still builds; it just won't run autonomously yet.

**Step 1 — Build the vault skeleton** in their vault: `My Journal/`, `AI Journal/` (one subfolder per agent lens they want), `_System/Brain/{wiki,raw}/`, plus folders for their sources.

**Step 2 — Process the sources** (write small per-user scripts — paths come from Step 0, never hard-coded):
- Claude Code `.jsonl` → one clean markdown per session (keep the user's prompts, drop tool-noise + excluded projects).
- claude.ai `conversations.json` → one markdown per conversation, **excluded keywords filtered over title AND body**.
- Their outcome metrics (CSV, analytics) → a per-topic rollup JSON.
- Split everything into per-item files + a processing queue with a cursor.

**Step 3 — Compile the wiki** with parallel subagents (Agent tool, a few entities each). Each reads the outcome-rollup + a few real source texts → writes one structured page (see "Stage 3" format below). Then build `index.md` + `SCHEMA.md`. Optionally a profile page from many subagents reading full bodies.

**Step 3.5 — Show the connections and get approval (do NOT skip — the user is promised this).** Before wiring up anything autonomous, surface the non-obvious connections you found while compiling, and let the user approve them ONE BY ONE. This is the moment they see the brain forming.
- As you compile, collect cross-source links worth flagging: a cluster (3+ pieces that are secretly one series), a refresh (old work + a live trend), a gap (something they built but never published), a bridge (a journal note that connects to old work), a contradiction (two pieces giving opposite advice).
- Present them as a short numbered list, plain language, each one sentence: *"Your trading posts and your finance builds are the same play — link them?"* / *"These three notes are secretly one series — merge?"*
- For each, ask **yes / no / edit.** Only build the approved ones into the wiki (add the cross-links + a thread/series page). Drop the rest.
- Then run ONE test pass of a single agent and show the user the output (a journal line + a wiki update) before anything goes on a schedule. Do not go fully autonomous until they've seen and okayed one real run.

**Step 4 — Wire each lens to its sources, then schedule it.** For every connection/lens the user chose in Step 0, write one agent. Each lens points at a specific slice of the finished wiki + raw data — that's the "what reads what" decision. Examples (map to whatever they picked):
- *what already worked* → reads the topic wiki pages + the outcome rollup + their published work queue.
- *what to build next* → reads their build/idea notes + the matching wiki page's money pattern + the web.
- *coach me* → reads their profile page + the last 2 days of their journal.
- *what to write next* → reads their best-pieces queue + the strategy wiki page + the web.

Each agent then runs the same loop (Stage 4): read index → drill into its wiki page(s) → pull from its queue → **compile into the wiki FIRST** → validate on web → write to its own journal folder → advance cursor. Register them with the scheduler (every few hours, offset so they don't collide, silent — plus one daily digest agent that messages a summary). This is the moment Hermes "goes into the wiki": after the wiki exists, each scheduled agent walks in through the index, reads its assigned pages, and writes back.

**Step 5 — Verify** one run end-to-end before leaving it autonomous: did the wiki update? did a journal line appear, in plain language, with a real number + a cited URL?

The stages below are the reference for each step. Read the relevant stage when you reach it; don't front-load it all on the user.

---

## The big idea (Karpathy's LLM Wiki + your own data)

Most "AI second brain" setups only think when you're sitting there asking. This one runs on a schedule and **compounds**. The pattern, from Andrej Karpathy's LLM Wiki (April 2026), has three layers:

1. **Sources** — raw material, never edited (your chats, your work, your numbers).
2. **Wiki** — LLM-*compiled* pages, one per topic. Read once, write a structured page, then *update* it — never recompute from scratch. This is the brain.
3. **Agents** — read the wiki + raw data on a schedule, surface insight, and **file good findings back into the wiki** so it gets smarter.

The model is a **compiler**: it reads your sources once, writes a page, and every future question reads the compiled page — cheap, fast, and it gets sharper over time.

---

## Stage 1 — Pull YOUR data out of Claude

The brain is only as good as what you feed it. Two goldmines most people never touch:

### Claude Code (terminal history)
Every Claude Code session is stored locally as JSON: `~/.claude/projects/<project>/<session>.jsonl`. Each line is an event — your prompts (`user`), Claude's replies (`assistant`), and the auto-generated title (`ai-title` → `aiTitle`). The rest is noise (tool calls, snapshots) to strip.

**Process it:** a script walks every `.jsonl`, keeps your *prompts* (the real signal — your decisions, what you built, what you tried), drops tool-noise and any private/client project (filter by folder name), and writes one clean markdown note per session with frontmatter (date, project, title). This becomes your **"building brain"** — what you actually made.

### Claude.ai (web/app history)
No local file — you export it: **Settings → Privacy → Export data** → emailed zip → `conversations.json` (often 1000s of conversations). Structure: an array of `{name, created_at, chat_messages:[{sender, content:[{type:"text", text}]}]}`.

**Process it:** a script flattens each conversation to your messages, tags it `thinking` vs `technical`, and writes one markdown per conversation. This is your **"thinking brain"** — how you reason, decide, feel.

> ⚠️ **Exclusion is mandatory.** Your export contains private/other-people's conversations. Filter them OUT by keyword over BOTH the title and the body (names, sensitive topics) before anything touches them. Be generous — better to drop a few real ones than leak a private one. Same for any client work.

### Your numbers (the outcome layer — the edge)
Karpathy's wiki uses articles/papers. **Yours have an outcome** — what made money, what got engagement, what converted. Export those metrics (CSV) and keep them as a source too. This is what turns "here's a topic" into "this topic earned X, that one earned nothing."

---

## Stage 2 — Processing techniques (raw → usable)

Raw exports are huge and messy. Three moves make them brain-ready:

1. **One file per item.** Split everything (each conversation, each note, each record) into its own small markdown. Never one giant file — agents should browse a *queue*, not re-read everything.
2. **Strip to signal.** Keep YOUR words and the decisions; drop tool-call noise, boilerplate, base64 junk, system messages. A tired reader (and a cheap model) should get each note in one pass.
3. **Join outcomes to content (code, not LLM).** A plain script rolls up your metrics per topic into one JSON (`topic → total $, avg engagement, top items, worst items`). This is free and exact — the LLM later reads these compiled numbers, not the raw spreadsheet every time.

Result: clean per-item notes + a money/outcome rollup + processing **queues** (with a cursor) so agents can walk a few items per run instead of drowning.

---

## Stage 3 — Compile the wiki (the brain)

This is the part the tutorials skip. You don't dump raw data into the agent — you **compile** it first.

- **One page per entity** — each tool, theme, person, project, or concept gets its own wiki page. Start with your ~15 biggest; let the system create new pages organically as new topics appear.
- **Compile with subagents (parallel).** Spawn several agents at once, each owning a few entities. Each reads that entity's outcome-rollup + a few real source texts → writes a structured page. Parallel = fast even over hundreds of sources.
- **Every page fuses content + outcome**, e.g.:
  ```
  # [Entity]
  ## What works   — pattern from the high-performing items (named, with numbers)
  ## What flopped — the low performers (named) so you stop repeating them
  ## Built / explored — links to the source notes
  ## The gap      — ONE thing the numbers reveal you haven't done
  ## Linked: [[other entities]]   ## Sources: [[items]]
  ## Updates:     — dated lines agents append later (NEVER silent rewrites)
  ```
- **An `index.md`** lists every page with a one-liner. The agent reads the index FIRST to find the right page, then drills in — it never reads the whole vault. This is the "layer map."
- **A `SCHEMA.md`** = the discipline doc: how to ingest, how to query, how to *lint* (the health check that finds contradictions and stale claims — the step that stops the wiki going shallow).

Special pages can be compiled differently — e.g. a **personality/profile page** built by many subagents each reading full conversation bodies to extract how you actually think and feel, then synthesized into one page.

---

## Stage 4 — Agents that read the wiki + data and analyze

Now the brain runs itself. Schedule agents (cron, a background runner — anything that fires on a timer). Each agent, every run:

1. **Reads the index → drills into the relevant wiki page(s)** (not the raw data — the compiled page).
2. **Pulls a few raw items from a queue** (cursor-based, so it walks the whole archive over days, then loops).
3. **Compiles into the wiki FIRST** — adds a dated Update to the right page, or creates a new page + indexes it. The brain grows every run.
4. **Validates against the live web** — searches Reddit/the web for proof the insight is real *right now*; cites the real URL + engagement, or honestly writes "not validated."
5. **Writes its finding to a journal** in plain language: the insight (with a real number) + why (linking the wiki page + source) + the web proof + one concrete next step.
6. **Advances the queue cursor**, saves.

Run different agents for different lenses on a rotation — e.g. one mines *what already worked*, one proposes *what to build next*, one reads your *journal/profile and coaches you*, one studies a *specific content format*. Each writes to its own journal folder, tagged, so you see exactly which lens produced what.

Keep them **silent by default** — they write to the vault; you read it when you want. One daily "digest" agent can summarize the night's findings to your phone (the only one that pings you). A chat layer (Telegram/Slack) lets you reference a finding and have an agent **carry it forward** with you — flesh out the build, draft the piece, find more proof — using the same compiled brain.

---

## The SOUL.md (the agent's identity — write this as a separate file)

Each agent needs an identity, not just a task. Karpathy calls it the schema; in practice it's a short `SOUL.md` that makes the model a disciplined brain-keeper instead of a generic chatbot. It's read on every run, so keep it tight. When you set this up for a user, fill this template with THEIR goal, voice, and data, and save it as its own file (separate from this recipe — it's read every run; the recipe isn't).

```markdown
# [Agent Name] — [one-line role tied to the user's goal]

You are the user's second brain. You read their vault and think for them on a schedule.
You report to [where output goes]. You never act outside the loop below.

## Who you are
- [A persona that fits the user — e.g. calm + data-driven + their domain].
- You generate INSIGHT/IDEAS grounded in their real numbers, never invented.
- You speak in [their voice / tone]. No flattery, no filler.

## The vault (your brain)
- Wiki (compiled truth): _System/Brain/wiki/  — read index.md first, then the right page.
- Sources: [their processed folders] · Outcomes: [their rollup].
- Journals you write to: AI Journal/[lens]/

## Hard boundaries
- NEVER read [excluded folders / private data / clients]. 
- NEVER invent a number, quote, or source. Unverified → leave out or say "not validated".
- Match by MEANING, not keywords (titles/topics are often creative).

## Your loop (every run)
1. Read index.md → drill into the 1-2 relevant wiki pages.
2. Pull the next items from your queue (cursor-based).
3. COMPILE into the wiki FIRST (dated Update, or a new page + index entry).
4. VALIDATE on the web; cite a real URL + engagement, or "not validated".
5. Write ONE journal line: **HH:MM [tag] — finding (with a real number)** / Why ([[wiki]]+[[source]]) / Web (URL) / Do (one next step).
6. Advance the cursor, save.

## Tone
Plain, concrete, useful. A tired person gets it in one read. Real numbers or it didn't happen.
```

This is the template. The user's installed agent fills it against their own conversations, numbers, and goal — which is exactly why it ends up sounding like *them*, not like a generic tool.

## Hard-won operating rules

- **The scheduler must be alive or nothing fires.** When the brain goes quiet, check the runner/gateway FIRST — a reboot or power cut silently kills scheduled jobs. Don't debug prompts before confirming the scheduler is up.
- **Match by MEANING, not keywords.** Before an agent calls something "missing" or "new," check the *topic*, not the words — you may have already covered it under a creative title. Re-suggesting your own past work is the #1 failure mode.
- **Compile before you write.** Every run: update the wiki, *then* write the journal from the updated wiki. Skip this and the brain stops compounding — it just chats.
- **Outcomes over vibes.** Tie every claim to a real number from your rollup. "This is a good angle" is worthless; "this theme earned X, that one earned nothing" is the brain.
- **Privacy is structural, not polite.** Exclude private/sensitive/client data at the *filter* level, not by asking the agent nicely. If it *can* read it, one day it will.
- **Watch the API budget.** Heavy days (big subagent runs + frequent agents) hit rate limits. A calm cadence (every few hours, not every few minutes) keeps it healthy and cheap.

---

## What you end up with

A vault where:
- Your Claude.ai + Claude Code history is clean, searchable, and private-filtered.
- A wiki of compiled, outcome-fused pages that **grows every run**.
- Agents that, while you sleep, read that wiki + your raw data + the live web and hand you grounded, numbered, sourced findings — different lenses, in plain language, with one next step each.

You're not building a Claude setup. You're building a second mind that runs without you — and gets smarter every day you feed it.
