# Building or refreshing `repos.yaml`

Follow this when the user asks to build, generate, refresh or review the repo map,
or when `repos.yaml` is missing. The goal is a draft the user reviews, not a final
answer, so mark everything inferred with its evidence and a confidence level.

This is read-only against the repos: don't change files, branches or remotes.
The only things you write are `repos.yaml` and `repos.REVIEW.md` at the workspace root.

## 1. Find the repos

The workspace root is the directory the user names, or the current directory.
Every immediate subdirectory containing `.git` is a repo; also check one level
deeper for grouped layouts such as `platform/` and `apps/`. Ignore `node_modules`,
`.venv`, build output and anything the user says to skip.

## 2. Collect the facts for each repo

Read or run whatever exists; skip what doesn't.

| Field | Where to look |
|---|---|
| `name` | GitHub name from the remote URL; fall back to the directory name |
| `path` | directory path relative to the workspace root |
| `remote` | `git remote get-url origin` |
| `default_branch` | `git symbolic-ref refs/remotes/origin/HEAD`, else `main` |
| `purpose` | README first paragraph, repo description, `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md` |
| `kind` | `infrastructure`, `api`, `ui`, `library`, `data`, `pipeline`, `docs`, `tooling` — from stack plus purpose |
| `stack` | manifests: `package.json`, `pyproject.toml`, `go.mod`, `pom.xml`, `*.csproj`, `*.tf`, `*.bicep`, `Dockerfile`, Helm charts |
| `verify` | test and lint jobs in `.github/workflows/*.yml`, `Makefile` targets, package scripts, `CONTRIBUTING.md` |
| `owners` | `CODEOWNERS` |
| `pr` | `.github/PULL_REQUEST_TEMPLATE.md`, labels used in templates or workflows |
| `provides` / `consumes` / `depends_on` | §3 |

A repo-level `CLAUDE.md` or `copilot-instructions.md` often states the purpose and
conventions outright; when it does, quote its path as the evidence and mark the
field high confidence.

## 3. Find the dependencies

Dependencies are the most valuable part of the map and the easiest to get wrong, so
keep evidence for every edge:

- **Published packages**: a library repo's package name appearing in another repo's
  manifest or lock file
- **APIs**: base URLs, OpenAPI or GraphQL specs, generated clients that point at a
  service another repo implements
- **Infrastructure**: Terraform `module` sources and `terraform_remote_state`, Bicep
  module references, Helm chart or container image names that match another repo,
  APIM API definitions that front another repo's service
- **CI/CD**: reusable workflows (`uses: org/repo/...`), `repository_dispatch`,
  deploy pipelines that check out or trigger other repos
- **Git**: submodules and subtrees
- **Docs**: README links to sibling repos, architecture diagrams

Record each edge as `depends_on` on the consuming repo. Fill `provides` with the
named things a repo exposes (`apim-gateway`, `orders-api`, `org-shared (pypi)`) and
`consumes` on the other side, so the names line up across repos.

A reference to a repo that isn't checked out is still worth recording: add it as a
stub entry with `path: null` and flag it in the review notes.

## 4. Write the draft

Write `repos.yaml` at the workspace root following `repos.example.yaml`. Keys that
start with `_` are ignored by the skill and `plan.py`, so use them for review notes
on every inferred field:

```yaml
    purpose: Terraform for the shared AKS and APIM platform
    _confidence: high          # high = stated in the repo, medium = strong signal, low = guess
    _evidence: "README.md line 3; terraform/main.tf"
```

Also write `repos.REVIEW.md` next to it containing:

- the dependency graph as a Mermaid diagram, with any cycle called out — a cycle
  usually means shared code that should be its own library
- open questions: repos with no clear purpose, references to repos that aren't
  checked out, repos with no verify commands, fields marked low confidence
- anything that looked like it shouldn't be in the map (archived repos, forks,
  scratch directories)

Then run `scripts/plan.py --validate` against the draft and fix what it reports.

## 5. Hand off

Summarize what you found, point at the open questions, and stop. After the user has
reviewed and corrected the file, offer to strip the `_confidence` and `_evidence`
lines; the skill reads `repos.yaml`, never the review notes.
