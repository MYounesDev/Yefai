---
name: sade-surdurulebilir-mimari
description: Yazılım mimarisinde sadelik, sürdürülebilirlik ve karmaşıklık yönetimi için karar, review, refactor ve öğretici rehberlik sağlar. Use when Codex needs to evaluate or design architecture for cognitive load, naming clarity, predictable control flow, cohesion/coupling, SOLID tradeoffs, GoF pattern selection, monolith vs microservices vs modular monolith, Clean/Hexagonal Architecture, idempotent data pipelines, quality gates, YAGNI, premature abstraction, or over-engineering risk.
---

# Sade Surdurulebilir Mimari

## Core Stance

Treat architecture as a tool for lowering long-term change cost, not as a place
to display patterns. Prefer the simplest structure that keeps business rules
understandable, testable, and separable from volatile infrastructure.

Use this skill to make design judgment explicit:

- reduce cognitive load before adding abstractions;
- keep high cohesion inside modules and low coupling between modules;
- let real change pressure justify boundaries, patterns, and distribution;
- prefer reversible, locally testable structures over speculative future-proofing;
- verify architecture claims with tests, dependency direction, and operational evidence.

## Workflow

1. Fingerprint the context.
   Identify whether the target is a throwaway script, prototype, production
   feature, enterprise module, data pipeline, integration boundary, monolith,
   modular monolith, microservice system, or distributed workflow.

2. Name the dominant complexity.
   Choose the primary pain: cognitive load, unclear names, surprising side
   effects, nested control flow, low cohesion, tight coupling, framework lock-in,
   boundary leakage, distributed-system overhead, non-idempotent processing,
   duplicated knowledge, or speculative abstraction.

3. Locate the real reason to change.
   For each module or boundary, ask which actor, policy, data source,
   integration, scale pressure, or operational constraint causes change. Do not
   split modules only because a pattern suggests it.

4. Pick the smallest architectural response.
   Prefer renaming, deletion, function/module extraction, dependency inversion,
   narrow ports, or a modular-monolith boundary before introducing new services,
   frameworks, factories, event systems, or broad inheritance hierarchies.

5. Check the abstraction gate.
   Add a pattern or layer only when it solves a named recurring problem, removes
   meaningful duplication of knowledge, protects a volatile boundary, or enables
   required independent testing, deployment, or scaling.

6. Define verification.
   State which tests, dependency checks, contracts, quality gates, traces, or
   operational metrics prove the design is simpler and safer.

## Review Checklist

Use these checks during architecture review or refactor planning:

- Cognitive load: Can a new maintainer build the mental model without jumping
  across many files, hidden side effects, or ambiguous names?
- Control flow: Are the main paths linear and predictable, or buried in nested
  conditions, callbacks, and exception-driven branches?
- Cohesion: Does each module serve one coherent capability or business concept?
- Coupling: Can one module change without forcing unrelated modules to change?
- Dependency direction: Do business rules depend on frameworks, databases,
  network protocols, or UI details?
- Interface size: Are clients forced to know operations or data they do not use?
- Substitution: Can alternative implementations satisfy the same contract
  without special-case checks?
- Topology: Is the chosen monolith, modular monolith, or microservice structure
  justified by team, deployment, scaling, and operational constraints?
- Data reliability: Are pipelines idempotent, restartable, observable, and
  protected by quality gates?
- Over-engineering: Is any layer, pattern, service, or optimization built for a
  guessed future rather than a current pressure?

## Decision Heuristics

- Prefer a modular monolith when the product is young, domain boundaries are
  still forming, or the team cannot afford distributed tracing, service
  contracts, and cross-service failure handling.
- Prefer microservices only when independent deployment, independent scaling,
  team ownership, or fault isolation clearly outweighs distributed complexity.
- Use Clean/Hexagonal Architecture at volatile boundaries where business rules
  must stay testable without databases, frameworks, queues, or HTTP.
- Use SOLID as a diagnostic language, not a checklist to maximize. KISS and
  YAGNI override SOLID ceremony when the current problem is simple.
- Use GoF patterns as named solutions to recurring problems. Avoid pattern use
  that mainly makes the code look more "architectural."
- In data pipelines, prioritize idempotency, schema validation, profiling,
  lineage, and quality gates before adding orchestration complexity.
- Optimize only after measurement shows a real bottleneck. Record the evidence.

## Pattern Selection

Reach for a pattern only after naming the failure mode:

- Factory: object creation varies and callers should not know concrete classes.
- Builder: construction has many valid steps or combinations that need clarity.
- Adapter: an external or legacy interface does not match the domain contract.
- Facade: a noisy subsystem needs a narrow, stable entry point.
- Strategy: algorithms vary and conditionals are growing around policy choice.
- Observer: multiple dependents need notifications without polling or tight
  coupling.
- Port/Adapter: the domain needs to call out to infrastructure through a stable
  contract that it owns.

## Output Shape

When answering, include:

- context fingerprint;
- dominant complexity;
- principle or pattern involved;
- recommended change;
- why the tradeoff fits now;
- what not to build yet;
- verification needed or already performed.

For code reviews, lead with concrete findings and file references. For design
advice, make the tradeoff explicit and prefer one actionable next step over a
catalog of possible architectures.

## References

Load `references/mimari-karar-rehberi.md` when the task needs deeper detail on
cognitive load, SOLID tradeoffs, cohesion/coupling, topology choices,
hexagonal architecture, pipeline reliability, or over-engineering heuristics.
