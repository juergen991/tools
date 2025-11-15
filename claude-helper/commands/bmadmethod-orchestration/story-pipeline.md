---
name: story-pipeline
description: Two-phase story pipeline for BMAD workflows
---

You are the STORY PIPELINE ORCHESTRATOR.

Execute BMAD story workflows sequentially.

## USAGE

**Planning:**
```
/juergen:story-pipeline plan 4-2 4-3 5-1
```

**Development (in NEW context):**
```
/juergen:story-pipeline develop 4-2 4-3 5-1
```

## PRE-EXECUTION CHECKS

1. Verify BMAD initialized: `docs/sprint-status.yaml` exists
2. Create output dir: `docs/juergen-pipeline/` if missing
3. Display current working directory

If checks fail, STOP and report.

## COMMAND: plan

For EACH story number:

1. **Read sprint status** (save BEFORE state)
```bash
cat docs/sprint-status.yaml
```

2. **Execute workflows**
```
/bmad:bmm:agents:sm create-story {story_number} and then story-context {story_number}
```

3. **Verify** (check AFTER state)
```bash
cat docs/sprint-status.yaml
```

4. **Create report:** `docs/juergen-pipeline/story-{N}-planning.md`
```markdown
# Story {N} - Planning

Date: {date}

## Before
```yaml
{sprint-status BEFORE or "not present"}
```

## After
```yaml
{story entry AFTER}
```

## Verification
- Story created: [YES/NO]
- Context created: [YES/NO]
- Status ready-for-dev: [YES/NO]

## Files
- Story: docs/stories/story-{N}.md
- Context: docs/stories/story-{N}.context.xml
```

5. **Display progress**
```
Story {N} - Planning Complete ✓
  Report: docs/juergen-pipeline/story-{N}-planning.md
  Status: ready-for-dev
```

### After all stories

**Create summary:** `docs/juergen-pipeline/planning-summary-{date}.md`
```markdown
# Planning Summary

Date: {date}
Stories: {list}

## Results
{for each story:}
- Story {N}: ✓ ready-for-dev
  - Report: story-{N}-planning.md
  - Files: story-{N}.md, story-{N}.context.xml

## Next
Start NEW chat, run:
/juergen:story-pipeline develop {same stories}
```

**Display summary**
```
===============================================
PLANNING COMPLETE
===============================================
Stories: {list}
Reports: docs/juergen-pipeline/

Next: Start NEW chat for development
  /juergen:story-pipeline develop {stories}
===============================================
```

## COMMAND: develop

For EACH story number:

1. **Load planning context**
```bash
cat docs/juergen-pipeline/story-{N}-planning.md
```

2. **Verify sprint status**
```bash
cat docs/sprint-status.yaml
```
Check story exists and has planning-complete status.

3. **Execute workflows**
```
/bmad:bmm:agents:dev develop-story {story_number} and then code-review {story_number} an then add Review-Notes to story and set Sprint-Status "done" 
```

4. **Verify completion**
```bash
cat docs/sprint-status.yaml
```

5. **Create report:** `docs/juergen-pipeline/story-{N}-development.md`
```markdown
# Story {N} - Development

Date: {date}

## Before
```yaml
{sprint-status BEFORE}
```

## After
```yaml
{story entry AFTER}
```

## Verification
- Development complete: [YES/NO]
- Code reviewed: [YES/NO]
- Story done: [YES/NO]

## Implementation
{brief summary}

## Files Modified
{list key files}

## Tests
{list test files}
```

6. **Display progress**
```
Story {N} - Development Complete ✓
  Report: docs/juergen-pipeline/story-{N}-development.md
  Status: done
```

### After all stories

**Detect completed epics**

For each unique epic (extract from story numbers):
```bash
cat docs/sprint-status.yaml
```
Check if ALL stories in epic are "done".

**Create summary:** `docs/juergen-pipeline/development-summary-{date}.md`
```markdown
# Development Summary

Date: {date}
Stories: {list}

## Results
{for each story:}
- Story {N}: ✓ done
  - Planning: story-{N}-planning.md
  - Development: story-{N}-development.md

## Completed Epics
{for each complete epic:}
**Epic {N}: COMPLETE**

All stories done. Run retrospective:
```
/bmad:bmm:agents:sm
*epic-retrospective epic-{N}
```

## In-Progress Epics
{for each incomplete epic:}
**Epic {N}: {done}/{total} stories**
- Done: {list}
- Pending: {list}
```

**Display summary**
```
===============================================
DEVELOPMENT COMPLETE
===============================================
Stories: {list}
Reports: docs/juergen-pipeline/

{for completed epics:}
Epic {N}: COMPLETE
  Action: Run retrospective manually
  /bmad:bmm:agents:sm
  *epic-retrospective epic-{N}

{for incomplete epics:}
Epic {N}: {done}/{total} stories
  Continue with remaining stories in new chat
===============================================
```

## ERROR HANDLING

**Sprint status not updating:**
```
/juergen:repair-sprint-status {story_numbers}
```

**Story fails:**
- Document failure
- Continue with other stories
- Report to user

## EXECUTION RULES

1. Run pre-execution checks first
2. Execute stories sequentially
3. Save reports after each story
4. Verify sprint-status.yaml after each story
5. Detect completed epics after development
6. Create comprehensive summaries
7. If errors occur, document and continue

Begin orchestration.
