---
name: repair-sprint-status
description: Repair sprint-status.yaml from pipeline reports
---

Repair sprint-status.yaml using Juergen pipeline reports.

## USAGE

```
/juergen:repair-sprint-status 4-2 4-3 5-1
```

Use when BMAD updates didn't persist in sprint-status.yaml.

## WORKFLOW

For each story number:

### 1. Read Pipeline Reports

```bash
cat docs/juergen-pipeline/story-{N}-planning.md
cat docs/juergen-pipeline/story-{N}-development.md
```

If report missing, skip that phase and report.

### 2. Extract Sprint Status

Both reports contain section: **"Full Sprint Status Content"**

Extract complete YAML. Use most recent version (prefer development).

### 3. Read Current Sprint Status

```bash
cat docs/sprint-status.yaml
```

### 4. Determine Action

**Story MISSING:** Add complete entry from reports
**Story INCOMPLETE:** Merge missing data from reports
**Story appears COMPLETE:** Verify consistency, update if needed

### 5. Update File

Merge/add story data into sprint-status.yaml. Preserve other entries.

### 6. Verify

```bash
cat docs/sprint-status.yaml
```
Confirm story is present and complete.

### 7. Report Results

```
Story {N}:
  Before: [missing/incomplete/complete]
  After: COMPLETE
  Planning: [restored/verified/not found]
  Development: [restored/verified/not found]
  Source: [planning/development/both]
```

## FINAL OUTPUT

```
===============================================
SPRINT STATUS REPAIR COMPLETE
===============================================

Stories: {list}

Results:
{for each story:}
Story {N}:
  Before: {status}
  After: COMPLETE
  Planning: {restored/verified}
  Development: {restored/verified}

Sprint Status: docs/sprint-status.yaml
Updated: YES

Verify: cat docs/sprint-status.yaml
===============================================
```

## ERROR HANDLING

**Reports missing:**
```
ERROR: Cannot repair story {N}
  Reports not found

Run pipeline for this story first.
```

**sprint-status.yaml missing:**
```
ERROR: Sprint status file not found
  Expected: docs/sprint-status.yaml

BMAD not initialized.
```

**Malformed reports:**
```
WARNING: Story {N} report found but missing status section
Skipping this story.
```

## WHEN TO USE

- Subagent updates didn't persist
- BMAD commands ran but didn't update file
- File system issues
- Manual verification needed

Reports serve as source of truth for recovery.
