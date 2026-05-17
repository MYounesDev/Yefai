# Commit Standards Reference

Use this reference when planning, auditing, or writing commit messages.

## Atomic Commit Rule

An atomic commit represents exactly one logical change that can stand on its own. It should be buildable, testable, reviewable, and revertable without dragging unrelated work with it.

Checks:

- One purpose: feature, fix, refactor, test, docs, build, style, or chore.
- All files in the commit are needed for that purpose.
- The commit does not depend on a later commit to compile or behave correctly.
- Reverting the commit would remove only that logical change.
- Reviewers can understand the change without reading unrelated diffs.

Reject:

- Giant "all changes" commits.
- Tiny noisy commits such as `wip`, `fix typo`, `more changes`, or `try again`.
- Mixed semantic intent, such as a new feature plus an unrelated production bug fix.
- Ignored files, generated caches, logs, local config, or secrets.

## Message Format

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
- Use a noun-like scope when a module, service, layer, package, or documentation area is clear.

Body rules:

- Add a body when the reason, risk, design tradeoff, migration behavior, or operational impact is not obvious.
- Explain why the change exists; do not restate the diff mechanically.
- Wrap body text around 72 characters when writing a full commit body.

Footer rules:

- Use standard trailers when useful: `Closes: #123`, `Refs: JIRA-421`, `Reviewed-by: Name`.
- Use `BREAKING CHANGE:` only for genuine compatibility breaks.
- Do not mark a breaking change unless the user or project authority allows it.

## Commit Types

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

## Examples

Good:

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

Bad:

```text
update files
bug fixed
wip
feat: changes
fix: final
```
