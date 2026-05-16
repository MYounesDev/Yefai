---
name: yazilim-prensipleri
description: Yazılım tasarımı, mimari değerlendirme, refactor planı veya code review sırasında SOLID, DRY, KISS, YAGNI, tasarım kalıpları ve mimari kalıplar açısından karar vermeye yardımcı olur. Use when Codex needs to explain, review, refactor, teach, or choose tradeoffs around SRP, OCP, LSP, ISP, DIP, DRY, KISS, YAGNI, false duplication, over-engineering, design patterns, architectural patterns, MVC, microservices, or event-driven architecture.
---

# Yazilim Prensipleri

## Core Workflow

Use this skill as a design judgment checklist, not as a rule-enforcement script.

1. Identify the current context: throwaway script, prototype, production feature, enterprise module, integration boundary, or distributed system.
2. Name the dominant pain: rigidity, fragility, immobility, viscosity, cognitive load, duplicated knowledge, over-engineering, speculative generality, or tight coupling.
3. Apply the smallest principle set that addresses that pain.
4. Prefer simple code until real change pressure justifies an abstraction.
5. State tradeoffs explicitly. If two principles conflict, explain which one wins in this context and why.
6. For code changes, preserve behavior first with tests when practical, then refactor one smell at a time.

## Decision Heuristics

- Prefer `KISS` and `YAGNI` for prototypes, one-off scripts, unclear requirements, or low-change code.
- Prefer `SRP`, `OCP`, and `DIP` when business rules change often, many teams touch the code, or regression risk is high.
- Prefer `ISP` and `LSP` around polymorphism, device/payment/provider abstractions, plugin systems, and integration boundaries.
- Apply `DRY` to duplicated knowledge, not merely similar-looking syntax.
- Allow duplication when similar code has different actors, different reasons to change, or only appears twice.
- Use the Rule of Three before extracting shared abstractions unless the domain rule is already clearly one shared concept.
- Treat design patterns as vocabulary and proven options, not decoration.
- Avoid new dependencies or heavy framework machinery unless the existing codebase already uses them or the problem truly needs them.

## Principle Checks

Use these prompts while reviewing or refactoring:

- `SRP`: Does this module have more than one actor or reason to change?
- `OCP`: Can a new case be added by extension, or must stable code be edited repeatedly?
- `LSP`: Can every subtype replace the base type without surprise exceptions, weakened guarantees, or special cases?
- `ISP`: Are clients forced to implement or depend on methods they do not use?
- `DIP`: Does core policy depend on infrastructure details, concrete frameworks, databases, APIs, or file systems?
- `DRY`: Is the same business rule represented in multiple places?
- `KISS`: Is the solution harder to read, debug, or operate than the problem requires?
- `YAGNI`: Is this abstraction or feature built for a guessed future rather than a current requirement?

## Pattern Selection

Reach for a pattern only after naming the recurring problem:

- `Factory Method`: object creation varies and callers should not know concrete classes.
- `Adapter`: existing systems have incompatible interfaces or data formats.
- `Facade`: a complex subsystem needs a narrow, stable entry point.
- `Observer`: multiple dependents need notification after state changes without polling or tight coupling.
- `Strategy`: algorithms vary at runtime and conditional branches are growing.
- `MVC`: UI, orchestration, and domain state are mixed together.
- `Microservices`: independent deployment and scaling matter more than operational simplicity.
- `Event-Driven Architecture`: services are blocked by synchronous chains, latency, or cascading failures.

## Output Guidance

When answering, include:

- the relevant principle or pattern names;
- the specific symptom observed;
- the recommended change;
- why that tradeoff fits the current context;
- tests or verification needed if code is modified.

For reviews, lead with concrete findings and file references. For teaching, use short analogies only when they clarify the decision.

## References

Load only the reference needed for the task:

- `references/solid.md`: detailed SOLID guide, software rot symptoms, SRP/OCP/LSP/ISP/DIP examples, and SOLID-vs-KISS/YAGNI tradeoffs.
- `references/dry-kiss-yagni.md`: DRY, KISS, YAGNI definitions, anti-patterns, false abstraction warnings, and practical examples.
- `references/patterns.md`: design vs architectural pattern distinctions, GoF-style pattern summaries, MVC, microservices, event-driven architecture, and pattern-selection table.
