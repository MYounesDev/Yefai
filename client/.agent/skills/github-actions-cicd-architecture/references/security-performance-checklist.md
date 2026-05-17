# Security and Performance Checklist

Use this reference to audit GitHub Actions workflows for security, reliability, cost, and maintainability.

## Security Defaults

- Add top-level `permissions: contents: read` unless a workflow truly needs broader rights.
- Grant write permissions at the narrowest job scope.
- Avoid `permissions: write-all`.
- Pin third-party actions to trusted versions. For high-risk workflows, consider SHA pinning.
- Prefer OIDC for cloud provider authentication instead of long-lived `AWS_ACCESS_KEY_ID`, service-account JSON, or similar static secrets.
- Use environment-scoped secrets for staging/production and require reviewers where release risk warrants it.
- Do not expose production secrets to pull requests from forks or untrusted branches.
- Do not echo secrets, full environment dumps, tokens, or cloud credentials.
- Avoid publishing artifacts, Docker images, or packages from untrusted PR code.
- Treat CI as a supply-chain attack surface, not just a test runner.

## Permissions Pattern

Use narrow defaults:

```yaml
permissions:
  contents: read
```

Open only the permission needed by a specific job:

```yaml
jobs:
  upload-sarif:
    permissions:
      contents: read
      security-events: write
```

## OIDC Pattern

Use OIDC when a workflow needs cloud access:

- Configure a trust relationship in the cloud provider.
- Restrict trust by repository, branch, environment, or workflow where possible.
- Request `id-token: write` only in the job that exchanges the token.
- Keep cloud credentials temporary and scoped to the deployment or test task.

```yaml
permissions:
  contents: read
  id-token: write
```

## Secrets and Environments

- Use repository secrets for low-risk, non-production CI needs.
- Use organization secrets for centrally governed shared values.
- Use environment secrets for staging/production and jobs requiring approval gates.
- Never store secrets in workflow files, scripts, generated logs, or artifacts.
- Keep mock or dummy secrets separate from production credentials.

## Performance and Cost Controls

- Add PR concurrency cancellation:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

- Cache dependencies from lockfiles.
- Prefer deterministic install commands such as `npm ci` or ecosystem equivalents.
- Shard expensive E2E/regression suites through `strategy.matrix`.
- Upload artifacts only when useful, and set short `retention-days`.
- Move expensive jobs from PR to `push`, `schedule`, or `workflow_dispatch` if they block developer feedback.
- Split workflows when one event model makes the file hard to reason about.

## Runner Limits and Escalation

Watch for:

- Jobs approaching hosted runner time limits.
- Out-of-memory failures from browser tests, JVM services, Docker Compose, or load generation.
- Disk exhaustion from Docker layers, browser assets, or build outputs.
- Matrix expansion nearing platform limits.
- Queue delays caused by too many heavy jobs.

Escalate to larger or self-hosted runners when:

- Standard runners cannot complete reliably.
- Private network access is required.
- Special hardware or long-running jobs are required.
- The cost model favors owned infrastructure over hosted minutes.

## Common Anti-Patterns

- Assuming jobs run in file order instead of using `needs`.
- Using broad default token permissions.
- Publishing artifacts or images from untrusted PRs.
- Running full E2E, regression, and performance tests on every commit.
- Masking flaky tests with repeated retries instead of fixing synchronization.
- Using cache as required state.
- Keeping old artifacts indefinitely.
- Using static cloud keys instead of OIDC.
- Putting deployment credentials in repository-level secrets when environment protection is needed.
- Copy-pasting the same workflow across many repositories instead of using reusable workflows.

## Review Questions

Ask these before approving workflow changes:

1. What event should run this work, and is that frequency justified by risk?
2. Which jobs can run in parallel, and which require `needs`?
3. What is the fastest safe fail-fast gate?
4. Can this workflow run without secrets on untrusted PRs?
5. Are token permissions minimal?
6. Are long-lived secrets avoidable through OIDC?
7. Are dependencies installed deterministically?
8. Will the workflow still pass with an empty cache?
9. Are failure artifacts sufficient for debugging?
10. Is the runner class appropriate for CPU, memory, disk, network, and duration?
