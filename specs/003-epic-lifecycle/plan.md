# Implementation Plan: Epic Lifecycle

**Branch**: `003-epic-lifecycle` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)

## Summary

Track features as epic issues with automatic lifecycle state transitions based on task completion.

## Technical Context

**Language/Version**: Bash (commands are markdown interpreted by Claude)  
**Primary Dependencies**: beads (`bd` CLI), git  
**Testing**: Self-hosted development validation  
**Target Platform**: macOS/Linux with Claude Code

## Project Structure

### Source Code Changes

```text
.claude/commands/
├── speckle.sync.md       # UPDATE: Create/update epic, link tasks
└── speckle.status.md     # UPDATE: Show epic progress

.speckle/scripts/
└── epics.sh              # NEW: Epic lifecycle helper functions
```

## Implementation Phases

### Phase 1: Epic Helpers

1. Create `epics.sh` with:
   - `create_epic()` - create epic issue from spec.md
   - `get_epic_id()` - retrieve epic ID from mapping
   - `update_epic_status()` - transition epic based on task states
   - `get_epic_progress()` - calculate completion percentage

### Phase 2: Sync Integration

2. Update `speckle.sync.md`:
   - Check for existing epic in mapping
   - Create epic if not exists (type=epic, description from spec)
   - Link all tasks to epic
   - Update epic status based on task states

### Phase 3: Status Enhancement

3. Update `speckle.status.md`:
   - Show epic name and current status
   - Show epic progress bar
   - Add `--epics` option for multi-epic view

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Beads doesn't support type=epic | Use type=feature with epic label |
| Circular dependencies | Epic depends on tasks, not vice versa |
