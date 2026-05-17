# Git Commit and Branch Plan - [HH:MM DD/MM/YYYY]

> This plan was created before local branch or commit execution.
> Review the branch and commit commands before applying them.

## Repository Snapshot

- Starting branch: `<current-branch>`
- Rollback base HEAD: `<head-hash>`
- Working tree summary: `<short status summary>`

## Branch Plan

- Category: `feature|bugfix|hotfix|release|sandbox`
- Source branch: `develop|main|release/*|<current-branch>`
- Target branch: `develop|main|release/*`
- Recommended branch: `category/TICKET_AB_short-description`
- Naming rationale: ...
- Rejected branch names:
  - `bad-name`: ...

## Excluded Files

| File | Reason |
| --- | --- |

## Commit Plan

### Commit 1: type(scope): imperative summary

- Files: `...`
- Why: ...
- Body bullets:
  - `- first concrete change`
  - `- second concrete change`
- Ordering rationale: ...
- Atomicity check: ...

### Commit 2: type(scope): imperative summary

- Files: `...`
- Why: ...
- Body bullets:
  - `- first concrete change`
  - `- second concrete change`
- Ordering rationale: ...
- Atomicity check: ...

## Branch Commands

```bash
# Create the planned branch from the approved source branch.
git switch <source-branch>
git switch -c category/TICKET_AB_short-description
```

## Commit Commands

```bash
# Clear accidental staged state before making atomic commits.
git reset

# Commit 1
git add path/to/file-a path/to/file-b && git commit -m "type(scope): imperative summary" -m $'- first concrete change\n- second concrete change'

# Commit 2
git add path/to/file-c && git commit -m "type(scope): imperative summary" -m $'- first concrete change\n- second concrete change'
```

## Rollback Commands

```bash
# Return commit history to the pre-plan base while preserving file changes.
git reset --soft <head-hash>

# If the new branch was created but no longer needed, switch back first.
git switch <starting-branch>
```

## Verification Commands

```bash
git status --short
git log --oneline -n <commit-count-plus-context>
git branch --show-current
```
