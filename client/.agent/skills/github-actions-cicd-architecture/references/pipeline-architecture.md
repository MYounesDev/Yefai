# Pipeline Architecture Reference

Use this reference for GitHub Actions workflow design and CI/CD architecture decisions.

## Core Concepts

- CI validates frequent integration into a shared branch by building, linting, and testing in an isolated environment.
- Continuous Delivery produces a releasable artifact and usually stops before production behind a manual gate.
- Continuous Deployment promotes changes to production automatically after all quality gates pass.
- A CI/CD pipeline should be deterministic, observable, reversible, and cheap enough to run at the required frequency.

## GitHub Actions Hierarchy

- Event: the trigger that starts a run, such as `pull_request`, `push`, `schedule`, `workflow_dispatch`, or `repository_dispatch`.
- Workflow: a YAML file under `.github/workflows/`.
- Job: an isolated runner allocation. Jobs run in parallel unless connected with `needs`.
- Step: sequential commands or action calls inside a job. Steps share the same runner filesystem.
- Action: reusable packaged logic, usually invoked with `uses: owner/repo@version`.
- Runner: the machine executing a job. GitHub-hosted runners are fresh and ephemeral for each job.
- Artifact: persisted build/test output that must survive runner teardown.

## Trigger Guidance

- Use `pull_request` for fast pre-merge quality gates against protected branches.
- Use `push` filtered to `main`, `master`, or release branches for trusted branch validation, build, release, image publication, and deployments.
- Use `schedule` for expensive scans, full regression, DAST, dependency audits, maintenance, and performance checks.
- Use `workflow_dispatch` for manual rollback, release promotion, one-off heavy tests, and operator-driven tasks.
- Use `repository_dispatch` only when an external system must trigger GitHub Actions through API.

## Job Graph Guidance

- Treat each workflow as a DAG.
- Add `needs` whenever job B requires outputs, artifacts, or success from job A.
- Keep independent checks parallel: lint, SAST, unit tests, consumer contracts, and API smoke tests can often run concurrently after setup.
- Split heavyweight suites with `strategy.matrix` and test sharding when the suite is deterministic enough to parallelize.
- Use `strategy.fail-fast: false` for diagnostic-heavy E2E matrices when one shard failing should not hide other browser/shard failures.

## Runner Strategy

- Use GitHub-hosted runners for low-ops, short-lived, standard web/API/test workloads.
- Use larger runners for heavy but still managed workloads requiring more CPU, RAM, disk, static IPs, or specific acceleration.
- Use self-hosted runners for private-network access, unusual hardware, long-running jobs, or heavy workloads where infrastructure control matters.
- Do not attach self-hosted runners to public repositories unless the security model explicitly handles untrusted pull requests.
- Remember common GitHub-hosted constraints: jobs are time-limited, matrix expansion is finite, and standard runners have limited CPU, RAM, and disk.

## Artifact and Cache Rules

- Use artifacts for intentional outputs: coverage reports, screenshots, logs, build packages, SARIF output, and deployable bundles.
- Upload debugging artifacts with `if: failure()` or `if: always()` where post-failure evidence is required.
- Keep artifact retention short unless audit requirements need longer retention.
- Use caches only for reproducible dependencies and build layers keyed from lockfiles or equivalent deterministic inputs.
- Do not treat cache as a source of truth. A clean run without cache should still pass.

## Reusable Workflow Guidance

- Use `workflow_call` to centralize standards across many services.
- Keep reusable workflows parameterized by language/runtime, test command, artifact path, environment, and deployment target.
- Avoid copy-pasted workflow logic across repositories when a shared organization policy exists.
- Keep repository-specific secrets and deployment behavior in the calling workflow or GitHub Environment configuration.

## GitHub Actions vs Traditional CI

Prefer GitHub Actions when:

- The repository already lives on GitHub.
- The project is cloud-native or standard web/API software.
- The team wants low infrastructure management.
- Workloads fit managed runner constraints.
- YAML-as-code reviewability matters.

Prefer Jenkins or another controlled CI platform when:

- Builds require unusual hardware, legacy systems, or air-gapped execution.
- Jobs exceed hosted runner time/resource constraints.
- The organization needs full network and plugin/runtime control.
- Existing regulated infrastructure already mandates on-prem CI.

