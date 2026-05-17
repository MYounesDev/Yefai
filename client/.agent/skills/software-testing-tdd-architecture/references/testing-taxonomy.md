# Testing Taxonomy And Quality Architecture

This reference condenses the source report
`Yazilim Testleri_ Felsefe, Evrim ve TDD.md` into operational guidance for
agents planning, reviewing, teaching, or implementing tests.

## Philosophy

Software quality is a design property. Debugging treats symptoms after they
appear; testing and verification create repeatable evidence and reduce the
chance that errors survive long enough to reach users.

Core problems solved by disciplined testing:

- Exponential defect cost: defects found earlier are cheaper to fix.
- Fear of change: regression suites allow safe refactoring and evolution.
- Cognitive load: tests externalize complex behavior and state space.

Dynamic tests cannot prove the absence of all bugs. For high-risk systems,
combine tests with static analysis, strong types, design by contract, invariants,
and formal modeling.

## Test Types

| Type | Scope | Use for | Checkout example |
| --- | --- | --- | --- |
| Unit | Function, class, isolated module | Fast business logic checks | Cart total, tax, coupon validity, rounding |
| Integration | Multiple components or infrastructure boundary | Database, cache, broker, filesystem, ORM, queue behavior | Add item persists correctly; payment event is published and consumed |
| Contract | Consumer-provider API interface | Microservice schema compatibility and independent deploys | Order service expects payment service fields and status codes |
| E2E | Full app from user perspective | Critical user journey continuity | Search product, add to cart, pay with sandbox card, see confirmation |
| Smoke | Broad shallow deployment health | Decide whether deeper testing is worth starting | App boots, checkout page returns 200, payment dependency responds |
| Sanity | Narrow focused patch validation | Confirm one fix behaves rationally | Credit-card expiry field accepts only valid month/year |
| Regression | Previously working behavior | Protect historical guarantees after change | New gift-wrap feature does not break shipping calculation |
| Acceptance | Business, legal, user acceptance | Confirm delivered value and rule compliance | Invoice tax matches accounting/legal expectations |
| Accessibility | DOM semantics, keyboard, screen reader, WCAG-style rules | Inclusive and legally safer UI | "Place order" button has role/name; no keyboard trap in modal |
| API/Security | Inputs, auth, authorization, abuse, business logic attacks | Prevent manipulation and unsafe state transitions | Reject negative cart totals; enforce idempotent payment retries |
| Performance/Stress | Capacity, latency, concurrency, resource limits | Find bottlenecks before traffic spikes | Thousands compete for final stock item without deadlock or oversell |

## Test Pyramid Guidance

Prefer many fast deterministic unit tests, fewer integration and contract tests,
and a small set of high-value E2E tests. Move a test upward only when the defect
cannot be caught reliably at a lower layer.

Common placement rules:

- Pure calculation belongs in unit tests.
- SQL, ORM mappings, constraints, transactions, and migrations belong in
  integration tests.
- Service schema drift belongs in contract tests.
- Browser-only flows, routing, focus handling, and full journey confidence
  belong in E2E or accessibility tests.
- Deployment viability belongs in smoke tests.
- Release confidence belongs in regression and targeted acceptance tests.

## TDD Guidance

TDD is a minute-by-minute design method:

1. Red: express desired behavior in a failing test before implementation.
2. Green: implement the smallest behavior that passes.
3. Refactor: improve design while tests protect behavior.

Use TDD when:

- the public interface is unclear
- a business rule has edge cases
- refactoring is risky
- dependencies need to be inverted
- behavior must become executable documentation

Do not skip refactoring. A project can have tests and still rot if the design is
not cleaned while the suite is green.

## Non-Test Verification

Use these when test cases would be an expensive or incomplete substitute for
design constraints:

- Strong/static types: prevent invalid combinations such as adding unrelated
  currencies or passing raw strings where validated IDs are required.
- Static analysis: catch unreachable code, unsafe calls, nullability errors,
  formatting violations, and suspicious patterns without running the program.
- Design by contract: document and enforce preconditions, postconditions, and
  invariants at boundaries.
- Schema validation: reject malformed API payloads before business logic.
- Formal verification/model checking: explore distributed interleavings,
  retries, timeouts, race conditions, and money movement before code exists.

For payment idempotency, test both "same key and same payload returns same
result" and "same key with different payload is rejected".

## Review Prompts

Use these questions during review:

- What user or business behavior does this test protect?
- Would the test fail for the bug it claims to prevent?
- Is the chosen layer the cheapest reliable layer?
- Is the test deterministic, isolated, and readable?
- Does it over-mock the behavior under test?
- Does it assert implementation details instead of visible behavior?
- Are failure messages useful enough to debug quickly?
- Does CI run this test at the right time?
- Are invalid states better prevented by types, contracts, or schemas?
- Are critical flows covered by at least one high-level journey or smoke gate?
