---
name: multi-repo-workflow
description: >
  Trunk-based feature workflow across the organization's related repositories
  (infrastructure, API, UI, shared libraries and others), driven by a repos.yaml
  map of where each repo lives, what it is for, and what it depends on. Use this
  whenever the user wants to start, continue, or ship a feature, fix, or ticket in
  any of the org repos; asks which repo a change belongs in; mentions a branch, a
  PR, or "main"; or wants the repo map built or refreshed — even when they never
  say "workflow" or name this skill.
---

# Multi-repo trunk-based workflow

Work in this organization spans several repositories that depend on each other.
Each repo has its own purpose, stack, test commands and reviewers, and every change
follows trunk-based development: a short-lived branch cut from a fresh `main`, a PR
back to `main`, and nothing committed to `main` directly.

The point of this skill is that the user never has to re-explain where the repos
are, what each one is for, or how PRs get raised. That knowledge lives in
`repos.yaml`; this skill says how to use it.

## 1. Load the repo map before anything else

Find and read `repos.yaml`. Look in this order:

1. `$MULTI_REPO_CONFIG`, if that environment variable is set
2. `repos.yaml` in the current directory, then each parent directory up to `$HOME`
3. `~/.config/multi-repo/repos.yaml`

The file is the single source of truth for repo paths, purposes, dependencies,
verify commands and PR settings; `references/repos.example.yaml` documents every
field. Treat its contents as fact and don't invent a purpose or dependency for a
repo that isn't listed — if the map looks wrong or incomplete, say so and ask.

`scripts/plan.py` reads the map for you: `--list` shows the repos, `--validate`
checks it for unknown dependencies and cycles, and passing repo names prints the
ordered plan used in the next step. Prefer it over reasoning about the YAML by hand.

If there is no `repos.yaml`, offer to generate one by following
`references/inventory.md`. Don't start feature work in repos you have no map for.

## 2. Scope the work and show a plan

From the request, work out:

- **Ticket or identifier.** Ask if there isn't one; it goes into branch names,
  commits and PR titles so every piece of the change is traceable.
- **Which repos are touched.** Decide from each repo's `purpose`, `provides`,
  `consumes` and `depends_on`. A change to an API contract usually touches the API
  repo and everything that `consumes` it; an infra change may touch nothing else
  but has to land first.
- **Order.** Dependencies first (`plan.py` does the topological sort). This is
  the order for branching, PRs and merges.

Before any git write operation, present a short plan:

```
Ticket: PLAT-1234
Branch: feature/PLAT-1234-rate-limit-headers
Repos (dependency order): platform-infra → core-api → web-ui
  platform-infra  add APIM rate-limit policy
  core-api        surface X-RateLimit-* headers
  web-ui          show remaining-quota banner
```

Wait for confirmation on the first plan of a session; after that, small
adjustments don't need re-approval.

## 3. Branch from a fresh main

For each touched repo, in dependency order:

```bash
cd <workspace_root>/<repo.path>
git status --porcelain                                     # must be empty — stop and ask if not
git fetch origin
git switch -c <branch> --no-track origin/<default_branch>
```

Use the same branch name in every repo the feature touches, so a reviewer can find
all parts of the change with one search. Build it from `defaults.branch_pattern`
(default `{type}/{ticket}-{slug}` — type is `feature`, `fix`, `chore` or `hotfix`;
slug is short kebab-case).

If the branch already exists locally or on origin, the user is probably resuming
work: switch to it and rebase onto `origin/<default_branch>` instead of creating a
duplicate. Never commit on the default branch, and don't branch from another
feature branch unless the user explicitly wants stacked work.

## 4. Implement inside each repo's own conventions

Every repo has rules of its own that this skill does not override. Before editing
in a repo, read whichever of these it has: `CLAUDE.md`, `AGENTS.md`,
`.github/copilot-instructions.md`, `CONTRIBUTING.md`, `README.md`. They win on
anything repo-specific (formatting, project structure, test layout); this skill
only governs the cross-repo flow.

Keep changes scoped to the ticket. Commit using `defaults.commit_pattern`
(conventional-commit style with the ticket id) so commits in any repo trace back
to the same piece of work.

When an upstream change (an API schema, a Terraform output) is required by a
downstream repo, say so in both PRs and prefer backward-compatible changes, so the
downstream repo keeps working while the PRs are in flight.

## 5. Verify before pushing

Run every command in the repo's `verify` list and fix failures before pushing.
If `verify` is empty, use the obvious equivalent (`make test`, `npm test`,
`pytest`, `terraform validate`, `dotnet test`) and tell the user you fell back to
it so they can add it to the map. Never push a repo whose verify step is failing
without telling the user.

## 6. Push and open PRs in dependency order

```bash
git push -u origin <branch>
gh pr create --base <default_branch> --title "<ticket>: <summary>" --body-file <tmp> \
  [--reviewer ...] [--label ...] [--draft]
```

- Fill the body from the repo's `pr.template` if it has one, else
  `defaults.pr_template`, else the structure below.
- Apply `pr.reviewers` and `pr.labels` from the map.
- Open upstream PRs first. Open downstream PRs as drafts when they can't merge
  until the upstream lands (`defaults.pr_draft_downstream`), and say why in the body.
- Once all PRs are open, cross-link them: edit each body to list the others with
  `gh pr edit --body-file`.

Default PR body when no template exists:

```
## What
<one paragraph>

## Why
<ticket link / context>

## Cross-repo
- platform-infra: #123 (merge first)
- web-ui: #45 (draft until this merges)

## Verification
- [ ] <verify commands run, with result>
```

Finish by listing the PR URLs in merge order.

## Guardrails

Mistakes in a multi-repo setup are expensive to unwind and often invisible until a
pipeline breaks, so:

- Ask before force-pushing, rebasing a branch that is already pushed and shared,
  deleting any branch, pushing to or merging into a default branch, or running
  anything in a repo not listed in `repos.yaml`.
- Never commit secrets, `.env` files or generated state (`*.tfstate`,
  `node_modules`, build output), even if the user's working tree contains them.
- Don't edit `repos.yaml` silently; propose the change.
- A dirty working tree when you arrive belongs to the user — stop and ask.

## Quick reference

| User says | Do |
|---|---|
| "Start PLAT-1234, rate-limit headers" | §1–3: load map, plan, branch in each repo |
| "Continue the rate-limit work" | find the branch by ticket across repos, rebase, resume |
| "Raise the PRs" | §5–6: verify, push, PRs in order, cross-link |
| "Which repo does X go in?" | answer from `purpose` / `provides` in the map |
| "Build / refresh the repo map" | follow `references/inventory.md` |
