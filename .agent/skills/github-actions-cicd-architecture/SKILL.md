---
name: github-actions-cicd-architecture
description: Design, review, or refactor GitHub Actions CI/CD workflows and test automation architecture. Use when Codex works on .github/workflows/*.yml or *.yaml files; plans CI/CD pipelines; chooses pull_request, push, schedule, workflow_dispatch, or repository_dispatch triggers; designs job dependencies, matrices, service containers, artifacts, caching, OIDC, permissions, environments, approval gates, runner strategy, or language-agnostic test stages; or audits GitHub Actions security, performance, cost, and anti-patterns.
---

# GitHub Actions CI/CD Architecture

## Overview

Use this skill to turn CI/CD requirements into secure, deterministic, cost-aware GitHub Actions workflows. Prefer small workflow files, explicit dependency graphs, least-privilege permissions, fast PR checks, and heavier validation on main, schedule, or manual gates.

The source knowledge for this skill comes from:

- `/home/furkan/Projects/EDA-2/GitHub Actions ve CI_CD Dokümantasyonu.md`
- `/home/furkan/Projects/EDA-2/GitHub Actions CI_CD Test Otomasyon Mimarisi.md`

## Reference Selection

- Read `references/pipeline-architecture.md` when designing workflow hierarchy, triggers, jobs, steps, runner choices, artifacts, reusable workflows, or GitHub Actions vs Jenkins tradeoffs.
- Read `references/test-automation-strategy.md` when mapping unit, security, contract, integration, API, smoke, E2E, accessibility, regression, performance, stress, or acceptance tests into CI events.
- Read `references/security-performance-checklist.md` when reviewing or hardening workflow security, permissions, secrets, OIDC, caching, concurrency, matrix strategy, runner limits, flaky tests, or cost risks.

## Operating Workflow

1. Inspect the repository first: languages, package managers, existing `.github/workflows`, test commands, lockfiles, Docker/service dependencies, deployment targets, and branch strategy.
2. Classify the requested work as one of: PR validation, main-branch release readiness, deployment, scheduled maintenance, manual recovery, security hardening, or workflow review.
3. Choose triggers from risk and cost:
   - `pull_request`: fast quality gates for code that may enter protected branches.
   - `push` to `main` or `master`: trusted branch validation, build, artifact creation, release, or deployment.
   - `schedule`: expensive, long-running, or broad scans such as full regression, DAST, dependency audits, and performance tests.
   - `workflow_dispatch`: manual rollback, acceptance gates, release promotion, or optional heavy tests.
   - `repository_dispatch`: external systems starting a workflow by API.
4. Model jobs as a DAG. Jobs run in parallel by default; add `needs` for required ordering. Steps inside one job run sequentially and can share that runner's workspace.
5. Keep PR checks fast. Put lint, SAST/SCA, unit, consumer contract, integration, API, and smoke checks before expensive E2E or performance work. Move long E2E, regression, DAST, and load tests to main, cron, or manual workflows unless the repo is small enough to keep PR feedback under the target window.
6. Add security defaults before convenience:
   - Top-level `permissions: contents: read` by default.
   - Add write permissions only at the narrow job that needs them.
   - Prefer OIDC for cloud access over long-lived secrets.
   - Use GitHub Environments for environment-scoped secrets and required reviewers.
7. Optimize only after preserving determinism: deterministic installs (`npm ci`, locked dependencies, equivalent package-manager strict modes), cache keyed from lockfiles, concurrency cancellation for repeated PR pushes, matrix/sharding for expensive suites, and artifacts for failure evidence.
8. Verify workflow syntax and behavior with the repo's available validators or dry-run tooling. At minimum, inspect YAML validity, branch/event filters, permissions, `needs`, `if` expressions, secrets exposure, and artifact paths.

## Design Defaults

- Treat GitHub-hosted runners as ephemeral. Persist only intentional outputs through `actions/upload-artifact`, package registries, caches, or deployment targets.
- Do not assume two jobs run sequentially because they are written in order. Use `needs`.
- Do not publish artifacts, Docker images, or packages from untrusted fork PR code.
- Do not echo secrets or print full environment dumps in logs.
- Do not use `permissions: write-all`.
- Do not run every heavyweight test on every commit by default.
- Do not hide flaky E2E tests with blind retries. Quarantine or fix the wait condition.
- Prefer reusable workflows (`workflow_call`) when multiple repositories or services need the same standard.
- Prefer service containers for real integration dependencies when Dockerized dependencies are stable and lightweight enough for GitHub-hosted runners.

## Output Shape

When designing or reviewing CI/CD, return:

- The intended event model and why each trigger is used.
- The job DAG and which jobs may run in parallel.
- Security decisions: permissions, secrets, environments, OIDC, and third-party action risk.
- Test placement by event: PR, main push, schedule, and manual.
- Cost/performance controls: cache, concurrency, matrix/sharding, runner type, artifact retention.
- Concrete YAML edits or workflow files when implementation is requested.
- Verification performed and remaining risks.
