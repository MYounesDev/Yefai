# Mimari Karar Rehberi

Derived from the project source document:
`../../../Yazılım Mimarisinde Sadelik ve Sürdürülebilirlik.md`.

## Table of Contents

- Core principle
- Cognitive load and maintainability
- SOLID as tradeoff language
- Cohesion and coupling
- Pattern use
- Topology decisions
- Clean and hexagonal architecture
- Data pipeline reliability
- Over-engineering gates
- Review prompts

## Core Principle

Sustainable architecture optimizes for human understanding, controlled change,
and operational recoverability. It is not the maximum use of patterns,
services, or abstractions.

Prefer designs where:

- business rules are easy to find and test;
- module names create an accurate mental model;
- side effects are explicit and near boundaries;
- dependencies point inward toward stable policy;
- boundaries correspond to real reasons to change;
- failure recovery is designed before scale complexity is added.

## Cognitive Load And Maintainability

Treat cognitive load as an architectural constraint.

High-risk symptoms:

- vague names such as `Manager`, `Processor`, `Handler`, or `Utils` without a
  clear domain role;
- deeply nested conditionals that hide the normal path;
- functions that look pure but perform network, database, filesystem, or queue
  side effects;
- modules that require reading many unrelated files before the main behavior is
  understandable;
- inconsistent local patterns that break reader expectations.

Prefer:

- specific domain names;
- top-down module organization from policy to details;
- explicit commands for side-effecting operations;
- simple linear flow with early exits where they clarify the happy path;
- stable local conventions over clever isolated design.

## SOLID As Tradeoff Language

Use SOLID to identify change pressure, not to maximize ceremony.

- SRP: split when a module has multiple actors or independent reasons to
  change. Do not split merely because a class is long.
- OCP: use extension points when new cases repeatedly edit stable code.
  Conditional logic is acceptable while cases are few and volatile.
- LSP: make contracts honest. A subtype or implementation must not require
  callers to add special-case checks or expect surprise exceptions.
- ISP: keep interfaces narrow. Avoid broad contracts that force clients to know
  operations they never use.
- DIP: make core policy depend on ports or abstractions when concrete
  infrastructure changes often or blocks testing.

KISS and YAGNI can override SOLID-driven structure when current behavior is
small, stable, and locally understandable.

## Cohesion And Coupling

High cohesion means the elements inside a module all serve one coherent
business capability. Low coupling means modules interact through narrow,
stable contracts and do not know each other's internal details.

Good boundary indicators:

- separate actors own the change;
- data has a clear lifecycle inside the boundary;
- invariants can be enforced locally;
- tests can exercise the capability without unrelated subsystems;
- integration happens through explicit contracts, not shared internals.

Bad boundary indicators:

- a module mixes business policy, storage, network calls, formatting, and
  logging decisions;
- a change to one domain forces edits in unrelated domains;
- callers pass or inspect internal data structures;
- boundaries were copied from a framework, not from the domain.

## Pattern Use

Patterns are vocabulary for recurring forces.

Use a pattern when it removes a named source of complexity:

- Factory hides creation variation.
- Adapter isolates incompatible external interfaces.
- Facade narrows a complex subsystem.
- Strategy replaces growing policy conditionals with interchangeable behavior.
- Observer decouples notification producers from multiple consumers.
- Command captures operations that need queuing, retry, audit, or undo.

Avoid patterns when they only add indirection. A simple function, module, or
explicit conditional can be the more sustainable design.

## Topology Decisions

Architecture topology is an organizational and operational tradeoff.

Prefer monolith when:

- speed of delivery matters more than independent deployment;
- the team is small;
- domain boundaries are still unclear;
- debugging and E2E testing need to stay simple.

Prefer modular monolith when:

- the deployment unit can remain single;
- domain boundaries are becoming clear;
- future extraction may be needed;
- teams need stronger internal ownership without distributed-system overhead.

Prefer microservices when:

- services require independent deployment or scaling;
- teams own services independently;
- failure isolation is a real requirement;
- the organization can support observability, contracts, retries, latency,
  distributed tracing, and operational incident response.

Do not choose microservices to make an unclear domain clearer. Clarify the
domain first, usually inside a modular monolith.

## Clean And Hexagonal Architecture

Use Clean or Hexagonal Architecture when business rules must be protected from
volatile delivery and infrastructure details.

Core idea:

- domain/application policy sits in the center;
- input adapters translate UI, HTTP, CLI, jobs, or messages into use cases;
- output ports are contracts owned by the core;
- output adapters implement those contracts for databases, files, APIs, queues,
  and other external systems.

Benefits:

- business rules can be tested without infrastructure;
- frameworks can change with less policy churn;
- boundary behavior becomes explicit;
- side effects are concentrated at adapters.

Costs:

- extra files and contracts;
- more indirection for simple CRUD;
- risk of artificial ports when there is no volatile boundary.

Use only where the boundary earns its keep.

## Data Pipeline Reliability

For ETL, ML, analytics, and ingestion pipelines, simplicity means restartable
and observable processing, not just fewer steps.

Require:

- idempotency: repeated runs produce the same final state without duplicate or
  corrupt records;
- quality gates: schema, range, nullability, freshness, and profile checks stop
  bad data early;
- lineage: inputs, transformations, outputs, and versions are traceable;
- checkpoints: long pipelines can recover without reprocessing everything
  unsafely;
- explicit ownership for source changes and downstream contracts.

Before adding orchestration complexity, verify the pipeline can reject bad
inputs and resume safely after partial failure.

## Over-Engineering Gates

Challenge every abstraction with these gates:

- Current pressure: What current, observed problem does this solve?
- Change frequency: How often has this actually changed?
- Boundary evidence: Is the separation based on domain ownership or just code
  shape?
- Replacement cost: Could this be rewritten cheaply when the future becomes
  real?
- Reader cost: How many jumps does the abstraction add for a maintainer?
- Test value: Does it make meaningful behavior easier to verify?
- Operational cost: Does it require new deployment, monitoring, tracing, or
  incident-handling burden?

Reject "just in case" layers, scale fantasies, premature optimization, and
framework-driven boundaries unless evidence justifies them.

## Review Prompts

Use these prompts in design reviews:

- What is the smallest design that keeps the business rule testable?
- Which part is most likely to change for a different reason?
- Which dependency would be painful to replace?
- Where can an invalid state enter the system?
- What side effect would surprise a reader?
- Which module owns each invariant?
- What evidence says this needs distribution, async messaging, or a new
  abstraction now?
- What verification would fail if this architecture regresses?
