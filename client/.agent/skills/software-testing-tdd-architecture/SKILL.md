---
name: software-testing-tdd-architecture
description: Software testing strategy, quality architecture, and TDD coaching for production systems. Use when Codex needs to plan, review, teach, or implement unit, integration, contract, E2E, smoke, sanity, regression, acceptance, accessibility, API/security, performance, or stress tests; design CI quality gates; apply test pyramid tradeoffs; validate payment/cart/idempotency-style flows; or use TDD, design by contract, strong types, static analysis, or formal-method thinking to shape maintainable software.
---

# Software Testing TDD Architecture

## Core Stance

Treat tests as part of the system architecture, not as cleanup after coding.
Use tests to reduce change fear, cognitive load, defect cost, and deployment
risk. Prefer a small number of well-placed tests that protect real behavior over
large brittle suites that only exercise implementation details.

When teaching or reviewing, distinguish these ideas:

- Debugging finds and fixes a symptom after it appears.
- Testing creates repeatable evidence about expected behavior.
- Quality architecture prevents invalid states from becoming easy to express.
- TDD is a design workflow, not just "write tests first".

## Workflow

1. Define the behavior contract.
   Identify the user/business outcome, system boundary, invariants,
   preconditions, postconditions, failure modes, and data consistency rules.

2. Choose the cheapest reliable verification layer.
   Start at unit level when the behavior is pure business logic. Move upward
   only when the risk lives at a boundary, integration, deployment, UI flow, or
   runtime capacity limit.

3. Map risks to test types.
   Use unit tests for algorithms, integration tests for storage and messaging,
   contract tests for service interfaces, E2E tests for critical user journeys,
   smoke tests for deploy viability, sanity tests for focused patch checks,
   regression suites for historical guarantees, acceptance tests for business
   rules, a11y tests for inclusive UI semantics, security/API tests for abuse
   paths, and performance/stress tests for capacity and concurrency.

4. Design CI gates by feedback speed.
   Put fast deterministic tests before slow suites. Fail early on formatting,
   static analysis, type checks, unit tests, smoke tests, and changed-area
   contract checks. Run broader regression, E2E, accessibility, and performance
   checks at targeted milestones or release gates.

5. Use TDD when design is still forming.
   Drive the interface from a failing test, implement the minimum production
   code to pass, then refactor while the suite is green. Do not skip the
   refactor step; without it, TDD only creates tested clutter.

6. Strengthen the design beyond dynamic tests.
   When tests would mainly check invalid data shapes, encode the rule in strong
   types, schema validation, static analysis, contracts, invariants, or compile
   time checks. For distributed concurrency and money movement, consider model
   checking or formal specification before implementation.

## Test Strategy Checklist

Before proposing or editing tests, fingerprint the system:

- critical path: payment, checkout, auth, data loss, compliance, safety, or UX
- architecture: monolith, modular monolith, microservices, event driven, UI-only,
  backend API, batch job, or distributed workflow
- dependencies: database, cache, message broker, third-party API, browser,
  filesystem, scheduler, payment gateway, or external auth
- risk type: calculation error, interface drift, race condition, idempotency
  failure, authorization bypass, accessibility blocker, performance bottleneck,
  flaky UI, regulatory mismatch, or regression
- observability: logs, traces, metrics, artifacts, screenshots, audit records,
  or generated reports needed to explain failures

Then produce a test plan that names:

- what is verified
- where it is verified
- why that layer is appropriate
- which dependencies are real, fake, mocked, or sandboxed
- what data setup is required
- how the test fails when the protected behavior breaks
- what should run locally, in pull requests, after deploy, and before release

## TDD Rules

Use the Red-Green-Refactor loop as a design loop:

1. Red: write the smallest failing test that describes a behavior from the
   caller's perspective.
2. Green: write only enough production code to satisfy that behavior.
3. Refactor: improve names, structure, duplication, boundaries, and dependency
   direction while tests remain green.

Prefer tests that assert public behavior, observable side effects, contracts,
and invariants. Avoid locking tests to private helpers, line-by-line
implementation, incidental mocks, or unstable timing.

If a unit test is hard to isolate, treat that friction as design feedback. Look
for hidden global state, direct network calls, direct database writes, time
dependency, random dependency, hard-coded configuration, or mixed business and
infrastructure logic.

## Payment And Checkout Heuristics

For cart, checkout, billing, inventory, or similar transactional workflows,
verify these explicitly:

- totals: tax, discount, currency, rounding, coupon limits, free shipping, and
  negative-price rejection
- inventory: reservation, release, oversell prevention, race conditions, and
  eventual consistency
- payment: idempotency keys, retry behavior, timeout recovery, duplicate charge
  prevention, partial failure, reconciliation, and 409-style conflict on key
  reuse with different payloads
- service contracts: request and response schemas between order, cart, payment,
  invoice, inventory, and notification services
- user journey: product selection, cart update, coupon, checkout, confirmation,
  invoice availability, and failure messaging
- compliance and access: authorization, audit records, accessible form labels,
  keyboard navigation, and screen reader semantics

## Output Shape

When creating a testing plan or review, include these sections unless the user
asks for a smaller answer:

- behavior contract and assumptions
- risk map
- proposed test layers
- concrete test cases
- CI or release gate placement
- TDD or refactoring guidance
- non-test safeguards such as types, contracts, static analysis, or formal
  modeling
- open questions and residual risk

For code changes, keep tests focused on the changed behavior and run the most
relevant local verification command available in the repo.

## Reference Loading

Read `references/testing-taxonomy.md` when you need a compact catalog of test
types, e-commerce checkout examples, TDD guidance, and non-test verification
techniques derived from the source report.
