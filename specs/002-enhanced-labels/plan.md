# Implementation Plan: Enhanced Labels

**Branch**: `002-enhanced-labels` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)

## Summary

Add rich automatic labeling when syncing tasks from tasks.md to beads. Labels enable filtering by feature, phase, story, and parallelizability.

## Technical Context

**Language/Version**: Bash (commands are markdown interpreted by Claude)  
**Primary Dependencies**: beads (`bd` CLI), git  
**Testing**: Manual validation via self-hosted development  
**Target Platform**: macOS/Linux with Claude Code  
**Project Type**: CLI tool extension (slash commands)

## Constitution Check

- [x] No external services added
- [x] No new dependencies  
- [x] Follows existing patterns
- [x] Graceful degradation

## Project Structure

### Source Code Changes

```text
.claude/commands/
├── speckle.sync.md       # UPDATE: Add label generation logic
└── speckle.status.md     # UPDATE: Add phase breakdown display

.speckle/scripts/
└── labels.sh             # NEW: Label generation helper functions
```

## Implementation Phases

### Phase 1: Label Generation Helpers

1. Create `labels.sh` with:
   - `slugify()` - convert text to label-safe format
   - `extract_phase_label()` - get phase from task context
   - `extract_story_label()` - get story from `[US#]` marker
   - `build_label_string()` - combine all labels for bd create

### Phase 2: Sync Command Update

2. Update `speckle.sync.md`:
   - Generate feature label from branch name
   - Generate phase label from current markdown header
   - Generate story/parallel labels from task markers
   - Pass labels to `bd create --labels`

### Phase 3: Status Enhancement

3. Update `speckle.status.md`:
   - Query issues grouped by phase label
   - Show per-phase completion percentages
   - Add `--by-story` option for story breakdown

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Beads doesn't support --label filter | Fall back to grep on list output |
| Too many labels | Prioritize and limit to 5 labels max |
| Special chars in phase names | Robust slugify function |
