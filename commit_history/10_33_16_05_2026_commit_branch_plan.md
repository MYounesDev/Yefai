# Commit and Branch Plan

**Timestamp**: 2026-05-16 10:33  
**Repository**: /home/furkan/Projects/Yefai  
**Starting Branch**: main  
**Rollback Base HEAD**: b25af7ae7048883ecdd99a5fef89924936a7ca97  

---

## Integration Decision

| Decision | Value |
|----------|-------|
| **Source Branch** | main |
| **Target Branch** | main |
| **Branch Category** | Direct commit (skill additions) |
| **Integration Model** | Atomic commits directly to main |
| **Merge Readiness** | Ready — skills are self-contained, no functional dependencies |

---

## Excluded Files

None. All new files in `.agent/skills/` are safe to commit.

---

## Atomic Commits

### Commit 1: Add write-api-reference skill

**Purpose**: Add reusable skill for writing Next.js API reference documentation.

**Type**: `chore`  
**Scope**: `.agent/skills`  
**Title**: `chore(skills): add write-api-reference skill`

**Body**:
- Skill for producing API reference documentation for Next.js.
- Auto-activation for API reference pages, functions, components, file conventions, directives, and config.
- Includes templates, rules, and workflow patterns for technical documentation.

**Files**:
```
.agent/skills/write-api-reference/SKILL.md
```

**Rationale**: Single, focused skill. Independent of other features.

**Command**:
```bash
git add .agent/skills/write-api-reference/SKILL.md
git commit -m "chore(skills): add write-api-reference skill"
```

---

### Commit 2: Add yazilim-prensipleri skill (Turkish software principles)

**Purpose**: Add Turkish-language comprehensive skill for software principles (SOLID, DRY, KISS, YAGNI) and design patterns.

**Type**: `chore`  
**Scope**: `.agent/skills`  
**Title**: `chore(skills): add yazilim-prensipleri skill with comprehensive references`

**Body**:
- Turkish language skill for software design principles (SOLID, DRY, KISS, YAGNI).
- Includes deep technical references with real-world examples, anti-patterns, and trade-offs.
- Covers design patterns, architectural patterns, and practical decision matrices.
- Enables code review and architectural guidance in Turkish context.

**Files**:
```
.agent/skills/yazilim-prensipleri/SKILL.md
.agent/skills/yazilim-prensipleri/agents/openai.yaml
.agent/skills/yazilim-prensipleri/references/dry-kiss-yagni.md
.agent/skills/yazilim-prensipleri/references/patterns.md
.agent/skills/yazilim-prensipleri/references/solid.md
```

**Rationale**: 
- Comprehensive skill with 3 reference documents
- Self-contained module
- Independent from other skills

**Command**:
```bash
git add \
  .agent/skills/yazilim-prensipleri/SKILL.md \
  .agent/skills/yazilim-prensipleri/agents/openai.yaml \
  .agent/skills/yazilim-prensipleri/references/dry-kiss-yagni.md \
  .agent/skills/yazilim-prensipleri/references/patterns.md \
  .agent/skills/yazilim-prensipleri/references/solid.md

git commit -m "chore(skills): add yazilim-prensipleri skill with comprehensive references"
```

---

## Branch Commands

No branch creation needed. All commits go directly to `main`.

---

## Commit Commands (Execute in order)

```bash
# Navigate to repo
cd /home/furkan/Projects/Yefai

# Commit 1: write-api-reference skill
git add .agent/skills/write-api-reference/SKILL.md
git commit -m "chore(skills): add write-api-reference skill"

# Commit 2: yazilim-prensipleri skill with references
git add \
  .agent/skills/yazilim-prensipleri/SKILL.md \
  .agent/skills/yazilim-prensipleri/agents/openai.yaml \
  .agent/skills/yazilim-prensipleri/references/dry-kiss-yagni.md \
  .agent/skills/yazilim-prensipleri/references/patterns.md \
  .agent/skills/yazilim-prensipleri/references/solid.md

git commit -m "chore(skills): add yazilim-prensipleri skill with comprehensive references"
```

---

## Rollback Commands

If rollback is needed after commit:

```bash
# Hard reset to baseline
git reset --hard b25af7ae7048883ecdd99a5fef89924936a7ca97

# Or, if already pushed, use reverts
# git revert -n <commit-2-sha>
# git revert -n <commit-1-sha>
# git commit -m "revert: remove newly added skills"
```

---

## Verification Commands

After all commits complete:

```bash
# Show recent commit history
git log -2 --oneline --format="%h %s"

# List all new skill files now tracked
git ls-files | grep "^\.agent/skills/write-api-reference/"
git ls-files | grep "^\.agent/skills/yazilim-prensipleri/"

# Verify file counts
echo "write-api-reference files:" && git ls-files | grep "^\.agent/skills/write-api-reference/" | wc -l
echo "yazilim-prensipleri files:" && git ls-files | grep "^\.agent/skills/yazilim-prensipleri/" | wc -l
```

---

## Summary

✅ **Plan Ready to Execute**

- Two atomic commits, each representing one logical addition
- Clear separation: two independent skills
- Conventional Commits format with type and scope
- All files staged explicitly (no `git add .` or `git add -A`)
- Rollback and verification procedures included
- Turkish and English documentation both represented
