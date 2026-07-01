# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Repository

- **Remote:** https://github.com/solduma/agentic_design_pattern.git
- **Default branch:** `main`

## Mandatory Workflow

Every task in this repo MUST follow these steps **in order**. Do not skip or reorder.

### 1. Plan
Produce a written plan for the work before touching code. Capture goals, scope,
assumptions, and the concrete changes required.

### 2. Divide independent tasks
Break the plan into tasks that have **no dependencies on each other** and can run
in parallel. List them explicitly.

### 3. Sequence complicated tasks
Break any complex or dependency-bound task into an **ordered sequence** of smaller
subtasks. Note which task each one blocks or is blocked by.

### 4. Register issues to GitHub
Create one GitHub issue per task (`gh issue create`). Each issue must state:
- Goal / acceptance criteria
- Owner (subagent)
- Dependencies (blocks / blocked-by), so the dependency graph is explicit

### 5. Fan out subagents in worktrees
Launch subagents **in parallel** for every task that has **no blocking
dependencies**. Each subagent works in its **own feature git worktree** (use
`isolation: "worktree"`) on a dedicated `feature/<issue-number>-<slug>` branch.
Do not start a task whose dependencies are unresolved — wait for them to merge first.

### 6. Complete an issue → PR → merge
When all requirements for an issue are met:
1. Open a PR (`gh pr create`) referencing the issue (`Closes #<n>`).
2. Resolve any merge conflicts **locally** (rebase/merge `main`).
3. Push the resolved branch.
4. Merge the PR.
5. Mark the issue resolved (auto-closed via `Closes #<n>`, or `gh issue close`).

### 7. Clean up
Delete the local and remote feature branch and remove the worktree:
```
git worktree remove <path>
git branch -D feature/<issue-number>-<slug>
git push origin --delete feature/<issue-number>-<slug>
```

## Conventions

- Branch naming: `feature/<issue-number>-<short-slug>`
- PR title references the issue; body includes `Closes #<issue-number>`.
- Never merge a task whose blocking dependencies are still open.
- Prefer parallel fan-out (step 5) for independent work; keep dependent work sequential.

## Git & GitHub

- Use the `gh` CLI for all GitHub operations (issues, PRs, merges).
- Commit or push only when a step above requires it.
- End commit messages with:
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`
