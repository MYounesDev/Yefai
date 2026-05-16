# Commit and Branch Plan
**Timestamp**: 2026-05-16 10:08  
**Repository**: /home/furkan/Projects/Yefai  
**Starting Branch**: main  
**Rollback Base**: d63f2ea34efd6a7031804e0b6bfa38b9923c6102  

---

## Integration Decision

| Decision | Value |
|----------|-------|
| **Source Branch** | main |
| **Target Branch** | main |
| **Branch Category** | Direct commit (minor documentation and tooling setup) |
| **Integration Model** | Atomic commits directly to main |
| **Merge Readiness** | Ready for direct commit — no functional dependencies |

---

## Excluded Files

None. All untracked files in `.agent/` are safe to commit.

---

## Atomic Commits

### Commit 1: Agent rules and project governance

**Purpose**: Add project-specific agent rules, governance gates, and architecture documentation.

**Type**: `docs`  
**Scope**: `.agent/rules`  
**Title**: `docs(agent): add agent rules and governance phases`

**Body**:
- Index of 8 rules covering scope, phases, data storage (Supabase), dataset splits, AI services, FastAPI integration, validation, and documentation.
- Provides governance gates and implementation phases for team alignment.
- Establishes architecture constraints and decision points for the Yefai project.

**Files**:
```
.agent/rules/00-index.md
.agent/rules/01-scope-and-phase-gates.md
.agent/rules/02-data-storage-and-supabase.md
.agent/rules/03-dataset-split-and-image-modeling.md
.agent/rules/04-ai-services-and-models.md
.agent/rules/05-mock-spare-parts-crisis.md
.agent/rules/06-api-fastapi-integration.md
.agent/rules/07-validation-and-testing.md
.agent/rules/08-documentation-and-change-control.md
```

**Rationale**: Project rules are governance documentation independent of reusable skills. Grouped for semantic clarity.

**Command**:
```bash
git add \
  .agent/rules/00-index.md \
  .agent/rules/01-scope-and-phase-gates.md \
  .agent/rules/02-data-storage-and-supabase.md \
  .agent/rules/03-dataset-split-and-image-modeling.md \
  .agent/rules/04-ai-services-and-models.md \
  .agent/rules/05-mock-spare-parts-crisis.md \
  .agent/rules/06-api-fastapi-integration.md \
  .agent/rules/07-validation-and-testing.md \
  .agent/rules/08-documentation-and-change-control.md

git commit -m "docs(agent): add agent rules and governance phases"
```

---

### Commit 2: Add corporate-git-ci-standards skill

**Purpose**: Add reusable skill for git, commit, and CI standards aligned with corporate best practices.

**Type**: `chore`  
**Scope**: `.agent/skills`  
**Title**: `chore(skills): add corporate-git-ci-standards skill`

**Body**:
- Provides atomic commit guidelines, conventional commits format, and branch strategy.
- Includes references for commit and branch standards, templates for commit planning.
- Enables consistent version control practices and traceability across team workflows.

**Files**:
```
.agent/skills/corporate-git-ci-standards/SKILL.md
.agent/skills/corporate-git-ci-standards/agents/openai.yaml
.agent/skills/corporate-git-ci-standards/assets/templates/commit_branch_plan.md
.agent/skills/corporate-git-ci-standards/references/branch-standards.md
.agent/skills/corporate-git-ci-standards/references/commit-standards.md
```

**Rationale**: Reusable skill, separate from project-specific rules. Self-contained and independently useful.

**Command**:
```bash
git add \
  .agent/skills/corporate-git-ci-standards/SKILL.md \
  .agent/skills/corporate-git-ci-standards/agents/openai.yaml \
  .agent/skills/corporate-git-ci-standards/assets/templates/commit_branch_plan.md \
  .agent/skills/corporate-git-ci-standards/references/branch-standards.md \
  .agent/skills/corporate-git-ci-standards/references/commit-standards.md

git commit -m "chore(skills): add corporate-git-ci-standards skill"
```

---

## Branch Commands

No branch creation needed. Commits go directly to `main`.

---

## Commit Commands

Execute in order:

```bash
# Commit 1
git add \
  .agent/rules/00-index.md \
  .agent/rules/01-scope-and-phase-gates.md \
  .agent/rules/02-data-storage-and-supabase.md \
  .agent/rules/03-dataset-split-and-image-modeling.md \
  .agent/rules/04-ai-services-and-models.md \
  .agent/rules/05-mock-spare-parts-crisis.md \
  .agent/rules/06-api-fastapi-integration.md \
  .agent/rules/07-validation-and-testing.md \
  .agent/rules/08-documentation-and-change-control.md

git commit -m "docs(agent): add agent rules and governance phases"

# Commit 2
git add \
  .agent/skills/corporate-git-ci-standards/SKILL.md \
  .agent/skills/corporate-git-ci-standards/agents/openai.yaml \
  .agent/skills/corporate-git-ci-standards/assets/templates/commit_branch_plan.md \
  .agent/skills/corporate-git-ci-standards/references/branch-standards.md \
  .agent/skills/corporate-git-ci-standards/references/commit-standards.md

git commit -m "chore(skills): add corporate-git-ci-standards skill"
```

---

## Rollback Commands

If rollback is needed:

```bash
# Rollback to before commits
git reset --hard d63f2ea34efd6a7031804e0b6bfa38b9923c6102

# Or, revert specific commits (if already pushed)
# git revert -n <commit-2-hash>
# git revert -n <commit-1-hash>
# git commit -m "revert: remove agent rules and skills"
```

---

## Verification Commands

After commits, verify:

```bash
# Check commit log
git log -2 --oneline

# Check that .agent/ is tracked
git ls-files | grep "^\.agent/"

# Verify file counts
git ls-files | grep "^\.agent/rules/" | wc -l
git ls-files | grep "^\.agent/skills/corporate-git-ci-standards/" | wc -l
```

---

## Summary

✅ **Plan Ready to Execute**

- Two atomic, independently meaningful commits
- Clear separation: rules (governance) vs. skills (reusable tooling)
- Conventional Commits format with scopes
- All files staged explicitly (no `git add .`)
- Rollback and verification commands included
