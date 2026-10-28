# The Harness Engineer — install in one prompt

A Claude Code skill that interviews you about your project, then designs the harness around it: CLAUDE.md, skills, MCP connectors, hooks, subagents, and dynamic workflows. It writes one plan, you approve it layer by layer, and it builds and verifies each layer before moving to the next.

It is a diagnostic, not a checklist. Most projects need three or four of the six layers, and the skill will tell you which ones to skip and why.

---

## Step 1 — download

Download **`harness-engineer.skill`** from this folder. It lands in your Downloads.

(A `.skill` file is a zip archive with the skill's instructions inside. Nothing runs on download.)

## Step 2 — paste this prompt into Claude Code

Open Claude Code in any project and paste:

```
I downloaded a Claude Code skill at ~/Downloads/harness-engineer.skill

Install it for me:
1. It is a zip archive. Unpack it so that ~/.claude/skills/harness-engineer/ ends up containing
   SKILL.md and the references/ folder that sits beside it.
2. Do not execute anything from inside the archive. Unpack only.
3. Open SKILL.md and confirm the frontmatter has a name and a description.
4. Tell me in two lines what the skill does and what will trigger it.
5. Remind me whether I need to restart Claude Code before I can call it by name.
```

Claude will unpack it, check it, and tell you what it found.

## Step 3 — restart, then use it

Skills load when a session starts, so restart Claude Code once. Then open the project you actually want to set up and say any of these:

- "help me set up my harness"
- "I keep repeating myself to Claude, what should I automate"
- "should this be a skill or a hook?"
- `/harness-engineer`

You do not have to name the skill. It triggers on the symptom.

---

## What happens when it runs

**It audits first.** Looks for an existing CLAUDE.md, skills, agents, hooks, MCP config, and reads enough of your project to ask an informed question. It will not ask you something it can look up.

**It interviews you, one question at a time.** Six areas, covering what you build, what repeats every week, what you keep correcting, what lives outside Claude, what you check by hand, and what has gone wrong before. It follows the interesting answer instead of marching through a form. Two to ten minutes depending on how tangled your project is.

**It writes `harness-plan.md` in your project.** Every layer gets a verdict, either BUILD, SKIP, LATER or PRESENT, alongside the symptom in your own words, what it costs, and how you will know it worked. Then it stops.

**You approve layer by layer.** It builds one, verifies it works, ticks the box, and asks about the next. Stop whenever you want. The plan file persists, so picking it up next week costs nothing.

## The part most people get wrong

The six layers are not a checklist to complete. They are treatments, and your week is the symptom list.

| What your week looks like | The layer that fixes it |
| --- | --- |
| Re-explaining the project every session | CLAUDE.md |
| Pasting the same multi-step procedure | A skill |
| Claude cannot see your Notion, site, or database | MCP |
| A rule it ignores sometimes, one that has already cost you | A hook |
| Checks you run by hand before shipping | Subagents |
| Six steps with a loop and a retry | A dynamic workflow |

If your project only justifies two of those, a good plan says so. Ask it to configure all six and it should push back.

## Requirements

Claude Code. No API key, no dependencies, nothing to install beyond the skill folder itself.

## If it does not trigger

Check the folder sits at `~/.claude/skills/harness-engineer/` with `SKILL.md` directly inside it, not nested one level deeper. Then restart Claude Code. If it still does not fire, call it explicitly with `/harness-engineer`.
