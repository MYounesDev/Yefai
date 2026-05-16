# Branch Standards Reference

Use this reference when proposing, auditing, or explaining branch usage and branch names.

## Branch Usage

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

Treat every branch as integration debt: keep it focused and close it quickly.

## Branch Categories

- `feature/`: new capability; usually from `develop` to `develop`.
- `bugfix/`: non-production defect; usually from `develop` or `release/*`.
- `hotfix/`: urgent production fix; from `main` or the tagged stable branch.
- `release/`: production candidate stabilization; from `develop`, then back to `main` and `develop`.
- `sandbox/`: temporary branch for controlled experiments; delete after use.

Protected long-lived branches:

- `main` or `master`: production-stable code. No direct commits.
- `develop`: integration branch. No direct feature work.

## Naming Standard

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

Compatible hyphen-only variant:

```text
feature/AUTH-102-password-reset-api
bugfix/CART-405-cart-total-calculation
hotfix/PAY-911-payment-gateway-timeout
```

Prefer the strict formula when the user asks for a corporate-standard branch name.
