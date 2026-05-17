---
name: corporate-git-ci-standards
description: Use when Codex must review, create, split, or rewrite commit messages; plan atomic commits; evaluate staged changes; propose branch names; decide when and where branches should merge; audit branch strategy; create a commit/branch plan under commit_history; or provide safe local terminal commands for branch creation and local commits.
---

# Corporate Git Commit and Branch Standards

Use this skill only for Git commit and branch work. Keep every output focused on commit quality, atomic history, branch purpose, and branch naming.

## Role

Act as a senior Version Control Manager and Git Workflow Architect. Optimize for readable history, traceability, atomic commits, short-lived branches, and branch names that reveal purpose, owner, and ticket context.

## Bundled Resources

- Read `references/commit-standards.md` when writing, auditing, splitting, or explaining commits.
- Read `references/branch-standards.md` when proposing, auditing, or explaining branch usage and branch names.
- Use `assets/templates/commit_branch_plan.md` as the base template for every `commit_history/` plan file.

## Core Rules

- Never push, force-push, or delete remote branches from this skill.
- Never recommend direct commits to protected branches such as `main`, `master`, or `develop`.
- Prefer short-lived branches tied to a clear work item.
- Treat every branch as integration debt: keep it focused and close it quickly.
- Treat every commit as an audit record: make it atomic, independently understandable, and reversible.
- Do not hide unfinished work in long-lived "zombie" branches.
- Do not use branch names like `test1`, `deneme`, `wip-benim-dalim`, `junk/*`, `benim-notlarim`, or other purpose-free labels.
- Combine repository-local instructions with this skill. If the repo requires a stricter commit protocol, keep this skill's atomicity and branch rules and satisfy the stricter local format too.
- Before creating a branch or making commits, create a Markdown plan under `commit_history/` and put the exact terminal commands in that plan.
- Do not run `git switch -c`, `git checkout -b`, `git add`, or `git commit` before the plan file exists.
- Never use `git add .`, `git add -A`, or `git commit -am` in generated plans; always stage explicit files for each atomic commit.

## Standard Workflow

When asked to prepare or audit commits/branches:

1. Inspect state with read-only commands first: `git status --short`, `git branch --show-current`, `git diff --stat`, and targeted `git diff`.
2. Identify the active branch category and whether it matches the work.
3. Decide the integration model, source branch, target branch, and merge readiness using the Branch Integration Decision Standard.
4. Separate changed files into logical, independently working commit groups.
5. Check for files that should not be committed: secrets, environment files, logs, caches, build outputs, personal IDE settings, or ignored files.
6. Capture the current `HEAD` hash and current branch for rollback notes.
7. Produce a timestamped plan file in `commit_history/` with the branch recommendation, integration decision, commit groups, terminal commands, rollback commands, and verification commands.
8. Verify the plan against the atomicity, branch naming, and merge readiness rules before recommending any `git switch -c`, `git add`, or `git commit` command.

## Plan File Requirement

For any task that involves creating a branch or committing changes, write a plan file before executing Git state-changing commands.

Plan path:

```bash
commit_history/$(TZ=Europe/Istanbul date +"%H_%M_%d_%m_%Y"_commit_branch_plan.md)
```

Plan creation requirements:

- Run `mkdir -p commit_history`.
- Record `git rev-parse HEAD` as the rollback base.
- Record `git branch --show-current` as the starting branch.
- Record the recommended branch name and why it matches the category.
- Record excluded files and why they must not be committed.
- Record every atomic commit with title, body bullets, files, ordering rationale, and exact command.
- Include "Branch Commands", "Commit Commands", "Rollback Commands", and "Verification Commands" sections.
- Tell the user where the plan was saved.

Minimum setup commands for the plan file:

```bash
mkdir -p commit_history
HEAD_HASH=$(git rev-parse HEAD)
START_BRANCH=$(git branch --show-current)
PLAN_FILE=$(TZ=Europe/Istanbul date +"commit_history/%H_%M_%d_%m_%Y_commit_branch_plan.md")
```

Write the completed Markdown plan to `$PLAN_FILE`. The exact write mechanism can vary by environment, but the resulting file must exist before any local branch or commit command is run.

Do not execute the plan automatically unless the user explicitly asked this skill to both plan and apply. Even then, create the plan first and execute only the commands from that plan.

## Atomic Commit Standard

An atomic commit represents exactly one logical change that can stand on its own. It should be buildable, testable, reviewable, and revertable without dragging unrelated work with it.

Atomic commit checks:

- One purpose: feature, fix, refactor, test, docs, build, style, or chore.
- All files in the commit are needed for that purpose.
- The commit does not depend on a later commit to compile or behave correctly.
- Reverting the commit would remove only that logical change.
- Reviewers can understand the change without reading unrelated diffs.

Anti-patterns:

- One giant "all changes" commit that mixes UI, database, docs, and unrelated fixes.
- Tiny noisy commits that are not independently useful, such as `wip`, `fix typo`, `more changes`, or `try again`.
- Mixed semantic intent, such as a new feature plus an unrelated production bug fix.
- Adding ignored files, generated caches, logs, local config, or secrets.

Use selective staging when multiple logical changes exist:

```bash
git add path/to/file-a path/to/file-b
git commit -m "type(scope): imperative summary"
```

Use partial staging only when a single file contains multiple unrelated changes:

```bash
git add -p path/to/file
```

## Commit Message Format

Use Conventional Commits by default:

```text
type(scope): imperative summary

Body explaining why the change exists, risks, assumptions, or operational impact.

Footer-token: value
BREAKING CHANGE: explicit migration impact when authorized
```

Title rules:

- Write in English unless the repository explicitly uses another language.
- Use imperative mood: `add`, `fix`, `remove`, `refactor`, `document`.
- Keep the title short and specific; aim for 50 characters when practical.
- Do not end the title with a period.
- Use a scope when a module, service, layer, package, or documentation area is clear.
- Use a noun-like scope: `auth`, `api`, `db`, `ui`, `docs`, `tests`, `deps`.

Body rules:

- Add a body when the reason, risk, design tradeoff, migration behavior, or operational impact is not obvious.
- Explain why the change exists; do not restate the diff mechanically.
- Wrap body text around 72 characters when writing a full commit body.

Footer rules:

- Use standard trailers when useful: `Closes: #123`, `Refs: JIRA-421`, `Reviewed-by: Name`.
- Use `BREAKING CHANGE:` only for genuine compatibility breaks.
- Do not mark a breaking change unless the user or project authority allows it.

## Commit Types

Use only recognized types:

- `feat`: new user-facing, API, module, component, or architectural capability; SemVer MINOR.
- `fix`: bug, crash, logic error, regression, or production/test defect; SemVer PATCH.
- `docs`: documentation-only change.
- `style`: formatting-only change with no behavior impact.
- `refactor`: structural improvement without new feature or bug fix.
- `perf`: performance improvement.
- `test`: add or correct tests.
- `build`: build system, package manager, or dependency change.
- `ci`: CI configuration change only when the user specifically asks about commit classification for CI files.
- `chore`: routine maintenance that does not affect production code or tests.

If a change appears to need multiple types, split it into multiple commits.

Good examples:

```text
feat(auth): add password reset token expiry

Limit reset links to a short lifetime so leaked links cannot be
reused after the support window.
```

```text
fix(cart): correct total calculation for discounts

Apply discounts before tax so checkout totals match the pricing
rules used by the payment service.
```

```text
docs(setup): document local database bootstrap
```

Bad examples:

```text
update files
bug fixed
wip
feat: changes
fix: final
```

## Commit and Branch Plan File Format

When asked to plan commits, create a branch, or prepare local Git commands from a dirty worktree, copy `assets/templates/commit_branch_plan.md` into the timestamped `commit_history/` plan file and fill every placeholder from the actual repository state.

Before including commands in the plan:

- Ensure ignored files are excluded.
- Flag suspected secrets or local-only files.
- Ensure a staged index will not accidentally include unrelated changes.
- If files are already staged, warn that `git commit` includes everything currently staged.
- Include `git reset` before the first planned atomic commit command when there is any chance unrelated files are already staged.
- Use the two-layer commit message form in actual commands: `git commit -m "<title>" -m $'- body bullet\n- body bullet'`.
- Keep branch creation local. Do not include `git push`, upstream tracking, or remote branch deletion commands.

## Branch Usage Standard

Open a branch for every meaningful change to protected or shared code:

- New feature or module.
- Bugfix found during development, QA, or release stabilization.
- Urgent production hotfix.
- Release stabilization.
- Short experiment branch that will be deleted.

Do not open or keep a branch for:

- Hiding unfinished work without a clear ticket or completion path.
- Static environments like `test`, `staging`, or customer-specific permanent branches.
- Personal notes, random experiments, or vague tasks.
- Long-running work that should be split into smaller deliverable slices.

## Branch Categories

Use these categories:

- `feature/`: new capability; usually from `develop` to `develop`.
- `bugfix/`: non-production defect; usually from `develop` or `release/*`.
- `hotfix/`: urgent production fix; from `main` or the tagged stable branch.
- `release/`: production candidate stabilization; from `develop`, then back to `main` and `develop`.
- `sandbox/`: temporary branch for controlled experiments; delete after use.

Protected long-lived branches:

- `main` or `master`: production-stable code. No direct commits.
- `develop`: integration branch. No direct feature work.

## Branch Integration Decision Standard

When asked what to do with a branch, decide the merge target and timing instead of only naming the branch. Prefer the repository's existing workflow when it is visible in branches, CI files, release docs, or AGENTS/project instructions. If no workflow is visible, default to short-lived GitHub Flow for deployable web/SaaS work and GitFlow only when the project clearly has scheduled releases, versioned distribution, or active `develop`/`release/*` branches.

### Merge Target Matrix

| Current work | Source branch | Merge target | When to merge |
| --- | --- | --- | --- |
| GitHub Flow feature or bugfix | `main` | `main` via PR/MR | Branch is short-lived, CI is green, review is approved, and `main` remains deployable after merge. |
| Trunk-based small change | `main` or very short-lived branch from `main` | `main` | Change is tiny, independently verified, guarded by feature flags when incomplete, and integrated at least daily. |
| GitFlow feature | `develop` | `develop` | Feature is complete or safely hidden, tests pass, review is approved, and it belongs to the next planned release. |
| GitFlow release stabilization | `develop` | `main`, then back-merge to `develop` | Release candidate passes QA, version/changelog/migrations are ready, and only release fixes remain. |
| GitFlow hotfix | `main` or production tag | `main`, then back-merge to `develop` and any active `release/*` branch | Production defect is urgent, fix is minimal, verification proves the incident path, and release notes/tagging are planned. |
| GitLab Flow environment promotion | `main` | `test` -> `staging`/`pre-production` -> `production` | Each environment gate passes in order; never skip directly to `production` unless repository policy explicitly allows it. |
| Sandbox experiment | `main` or `develop` | No merge by default | Convert to `feature/*` or `bugfix/*`, write a plan, and verify the work before merging anywhere shared. |

### Merge Readiness Gates

Do not recommend merging into `main`, `master`, `develop`, `release/*`, or environment branches until all applicable gates are satisfied:

- The branch is up to date enough with its target to keep conflict risk low.
- CI, lint, typecheck, tests, and relevant static analysis pass or the plan explicitly records why a check is unavailable.
- The diff is atomic and reviewable; unrelated changes are split before merge.
- Required review, issue/ticket linkage, and release approval are satisfied.
- Secrets, local config, caches, logs, build outputs, and personal IDE files are excluded.
- Database migrations, feature flags, rollback path, and operational impact are documented when relevant.
- For `main`/production-bound work, the resulting target must be deployable immediately or explicitly held behind a safe feature flag.

### Main, Develop, and Release Decisions

- Merge to `main` only when the target is production-stable, CI/review gates pass, and the repository's workflow treats `main` as deployable or releasable.
- Merge to `develop` when the repository uses GitFlow-style integration and the work is intended for the next release, not immediate production.
- Merge `release/*` to `main` only after release stabilization is complete; then back-merge release fixes to `develop` so future work does not lose them.
- Merge `hotfix/*` to `main` first because production must be repaired from the production-stable line; then back-merge the same fix to `develop` and active release branches.
- Do not merge directly from a personal, vague, or sandbox branch into protected branches. Rename or recreate it under a valid category and document the plan first.
- If the branch has lived for multiple days or accumulated broad changes, prefer synchronizing with the target, splitting commits, and merging smaller slices rather than waiting for one large PR.

## Branch Naming Standard

Preferred strict formula:

```text
category/<ticket-id>_<initials>_<short-kebab-description>
```

Rules:

- `category` must be one of the allowed branch categories.
- `ticket-id` should come from Jira, Azure DevOps, Asana, Trello, incident tracking, or the team's issue system.
- Use `no-ref` only when no work item exists and the user accepts that limitation.
- `initials` identifies the developer or responsible owner.
- `short-kebab-description` must be short, English, lowercase, and kebab-case.
- Use `/` after the category so Git hosting tools group branches cleanly.
- Avoid underscores inside the description; reserve underscores for separating ticket, initials, and description.

Examples:

```text
feature/JIRA-421_AB_create-new-button-component
bugfix/123456_MS_fix-problem-a
hotfix/INC-911_EF_database-deadlock-resolution
release/v2.4.0
sandbox/no-ref_AB_test-cache-key
```

If the source guide or repository prefers hyphen-only ticket names, accept this compatible variant:

```text
feature/AUTH-102-password-reset-api
bugfix/CART-405-cart-total-calculation
hotfix/PAY-911-payment-gateway-timeout
```

Prefer the strict formula when the user asks for a corporate-standard branch name.

## Branch Recommendation Output

When asked to name or audit a branch, return:

```markdown
## Branch Recommendation

- Category: `feature|bugfix|hotfix|release|sandbox`
- Source branch: `develop|main|release/*|...`
- Target branch: `develop|main|...`
- Merge decision: `merge now|do not merge yet|promote through environments|convert branch first`
- Merge readiness: `ready|blocked`, with the missing gate if blocked
- Recommended name: `category/TICKET_AB_short-description`
- Rationale: ...
- Reject: `bad-name` because ...
```

## Compliance Report Format

When auditing commit and branch compliance, return:

```markdown
## Git Commit and Branch Audit

### Pass
- ...

### Findings
| Severity | Area | Evidence | Required Fix |
| --- | --- | --- | --- |

### Proposed Fixes
- Branch: `...`
- Commit: `...`

### Verification
- ...
```

Severity labels:

- `Critical`: secret in commit plan, direct protected-branch commit, force-push/shared-history risk.
- `High`: non-atomic commit plan, vague branch without ticket, mixed unrelated work.
- `Medium`: weak scope/type, long or unclear branch description, missing body for risky change.
- `Low`: wording, casing, or polish issue.
