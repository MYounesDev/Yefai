# Test Automation Strategy Reference

Use this reference to place test types into the right GitHub Actions events and job graph.

## Placement Matrix

| Test type | Preferred trigger | Rationale | Cost |
| --- | --- | --- | --- |
| Unit | `pull_request`, `push` | Fast fail-fast validation of isolated logic | Very low |
| Lint/style | `pull_request`, `push` | Cheap consistency and syntax gate | Very low |
| SAST/SCA | `pull_request`, `schedule` | Shift-left security plus deeper periodic scanning | Low/medium |
| Consumer contract | `pull_request` | Detect API expectation breaks before merge | Low |
| Integration | `pull_request` after unit | Validate DB/cache/queue boundaries with service containers | Medium |
| API functional | `pull_request`, `push` | Validate HTTP contract and critical endpoint behavior | Medium |
| Smoke/sanity | `pull_request` or `push` before deploy | Check critical paths before heavier validation or release | Low |
| E2E | `push` to main, `schedule`; PR only for small suites | High-value but slow and flaky if overused | High |
| Accessibility | `push`, `schedule`, or E2E subset | Automated WCAG/DOM checks catch only part of accessibility risk | Medium |
| Regression | `schedule` | Broad historical behavior validation | Very high |
| Performance/stress | `schedule`, `workflow_dispatch` | Long-running and resource-heavy load validation | Very high |
| Acceptance/UAT | `workflow_dispatch` or environment approval | Human/business approval gate | Manual |

## PR Quality Gate

Target a fast, reliable feedback loop. A good PR gate normally includes:

1. Checkout.
2. Runtime setup with deterministic dependency install.
3. Lint/static analysis.
4. Unit tests.
5. SAST/SCA where runtime cost is acceptable.
6. Consumer contract tests for service consumers.
7. Integration tests with lightweight service containers.
8. API smoke or functional tests.
9. Failure artifacts such as coverage, logs, and screenshots.

Avoid full regression, full E2E, load tests, long DAST, and deployment publishing from untrusted PRs.

## Main Branch Validation

After merge to `main` or `master`, the code is trusted enough for:

- Build/package/image creation.
- Provider contract verification.
- Broader smoke tests.
- E2E suites with sharding.
- Accessibility checks.
- Staging deployment.
- Release artifact upload or image publication.

Use `needs` so deploy or publish jobs cannot run until build and required validation jobs pass.

## Scheduled and Manual Work

Use `schedule` for:

- Full regression.
- Long DAST.
- Dependency update checks.
- Expensive SAST/SCA variants.
- Performance and stress tests.
- Cleanup and maintenance jobs.

Use `workflow_dispatch` for:

- Optional heavy tests.
- Rollback by input version.
- Release promotion.
- Acceptance testing.
- Incident response workflows.

## Service Containers

Use `services` for Dockerized dependencies such as PostgreSQL, Redis, queues, and local emulators when:

- The integration boundary is important.
- Mocking would hide meaningful failures.
- The service starts reliably in GitHub-hosted runner limits.
- Health checks can make startup deterministic.

Include explicit health checks for databases and network services before tests connect.

## E2E and Accessibility

- Keep E2E suites focused on critical user journeys.
- Use Playwright, Cypress, Selenium, or project-native tooling based on existing repo choices.
- Shard large suites by matrix and keep artifacts for failed shards.
- Use accessibility automation such as axe-core, pa11y, or Lighthouse as a signal, not a replacement for manual review.
- Avoid fixed sleeps in UI tests; use explicit waits for UI/network state.

## Performance Testing

- Prefer k6 for CI load testing when runner resources are constrained because it is generally lighter than thread-heavy JMeter workloads.
- Use JMeter only when the existing test estate or protocol support justifies its overhead.
- Keep performance and stress tests on scheduled/manual triggers or dedicated runners.
- Do not interpret results from an overloaded runner as application bottlenecks without checking runner CPU, RAM, and network saturation.

