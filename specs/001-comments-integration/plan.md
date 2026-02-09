# Implementation Plan: Beads Comments Integration

**Branch**: `001-comments-integration` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)

## Summary

Add automatic progress tracking via beads comments. When tasks are implemented, record what was done. Provide manual progress notes command for mid-implementation context.

## Technical Context

**Language/Version**: Bash (commands are markdown with embedded bash/JS pseudocode interpreted by Claude)  
**Primary Dependencies**: beads (`bd` CLI), git  
**Storage**: Beads issue comments (via `bd comments add`)  
**Testing**: Manual testing via self-hosted development (using Speckle to develop Speckle)  
**Target Platform**: macOS/Linux with Claude Code  
**Project Type**: CLI tool extension (slash commands)  
**Performance Goals**: Comment recording < 1 second  
**Constraints**: Must not block implementation workflow on comment failures  
**Scale/Scope**: Single developer, AI-assisted workflow

## Constitution Check

*GATE: Must pass before implementation.*

- [x] No external services added (beads already integrated)
- [x] No new dependencies (uses existing bd CLI)
- [x] Follows existing patterns (extends current commands)
- [x] Graceful degradation on failures

## Project Structure

### Documentation (this feature)

```text
specs/001-comments-integration/
├── spec.md              # Feature specification
├── plan.md              # This file
└── tasks.md             # Task breakdown (next step)
```

### Source Code Changes

```text
.claude/commands/
├── speckle.implement.md  # UPDATE: Add completion comment recording
├── speckle.progress.md   # NEW: Manual progress notes command
└── speckle.status.md     # NEW: Show task status with recent comments

.speckle/scripts/
└── comments.sh           # NEW: Helper functions for comment formatting
```

**Structure Decision**: Extend existing command structure. Add one new helper script for comment formatting to keep commands DRY.

## Implementation Phases

### Phase 1: Core Comment Recording

1. Create `comments.sh` helper script with:
   - `format_completion_comment()` - formats implementation completion data
   - `format_progress_note()` - formats manual progress notes
   - `add_comment_safe()` - wrapper that handles failures gracefully

2. Update `speckle.implement.md`:
   - After implementation, gather git diff stats
   - Call `format_completion_comment()` 
   - Record via `bd comments add`
   - Continue even if comment fails

### Phase 2: Progress Command

3. Create `speckle.progress.md`:
   - Accept freeform note as argument
   - Find current in-progress task from mapping
   - Format and record progress note
   - Error if no task in progress

### Phase 3: Status Enhancement

4. Create `speckle.status.md`:
   - Show current feature/epic progress
   - For each in-progress task, show most recent comment
   - Summary of completed vs remaining tasks

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| `bd comments` not available | Check command exists before use, warn but continue |
| Large diffs overflow comment | Truncate file list to 20, show totals only |
| No task in progress | Clear error message with guidance |

## Complexity Tracking

No constitution violations. Feature is a straightforward extension of existing functionality.
