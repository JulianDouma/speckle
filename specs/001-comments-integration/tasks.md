# Tasks: Beads Comments Integration

**Input**: Design documents from `/specs/001-comments-integration/`
**Prerequisites**: plan.md, spec.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Foundation

**Purpose**: Create shared comment formatting utilities

- [ ] T001 Create `.speckle/scripts/comments.sh` with comment helper functions

---

## Phase 2: User Story 1 - Record Implementation Progress (Priority: P1) 🎯 MVP

**Goal**: Automatically record what was done after each implementation

**Independent Test**: Implement any task, verify comment appears on bead issue

### Implementation for User Story 1

- [ ] T002 [US1] Add `format_completion_comment()` to comments.sh - formats files changed, lines, timestamp
- [ ] T003 [US1] Add `add_comment_safe()` to comments.sh - wrapper with graceful failure handling
- [ ] T004 [US1] Update `speckle.implement.md` to gather git diff stats after implementation
- [ ] T005 [US1] Update `speckle.implement.md` to record completion comment via `bd comments add`

**Checkpoint**: Implementations automatically record progress comments

---

## Phase 3: User Story 2 - View Implementation History (Priority: P2)

**Goal**: Show task status with recent implementation activity

**Independent Test**: Run `/speckle.status` and see task progress with comments

### Implementation for User Story 2

- [ ] T006 [US2] Create `speckle.status.md` command skeleton
- [ ] T007 [US2] Implement feature progress display (tasks completed vs total)
- [ ] T008 [US2] Add recent comment display for in-progress tasks

**Checkpoint**: Can view feature progress and implementation history

---

## Phase 4: User Story 3 - Manual Progress Notes (Priority: P3)

**Goal**: Allow manual progress notes during implementation

**Independent Test**: Run `/speckle.progress "note"` and verify comment added

### Implementation for User Story 3

- [ ] T009 [US3] Create `speckle.progress.md` command
- [ ] T010 [US3] Add `format_progress_note()` to comments.sh
- [ ] T011 [US3] Implement current task detection from mapping file
- [ ] T012 [US3] Add error handling for no task in progress

**Checkpoint**: Can add manual progress notes during implementation

---

## Phase 5: Polish

**Purpose**: Documentation and validation

- [ ] T013 [P] Update README.md with new commands
- [ ] T014 [P] Update docs/SELF-HOSTING.md with v0.2.0 entry
- [ ] T015 Self-validate: Use `/speckle.progress` during own development

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Foundation)**: No dependencies - start immediately
- **Phase 2 (US1)**: Depends on T001 completion
- **Phase 3 (US2)**: Can start after Phase 1, independent of US1
- **Phase 4 (US3)**: Can start after Phase 1, independent of US1/US2
- **Phase 5 (Polish)**: After all user stories complete

### Within Each Phase

- T002, T003 can run in parallel (different functions)
- T004, T005 are sequential (T005 uses output of T004)
- T006, T007, T008 are sequential (building same command)
- T009-T012 are sequential (building same command)

---

## Notes

- Each user story is independently valuable
- US1 is the core MVP - provides memory across sessions
- US2/US3 enhance but aren't required for basic functionality
- Self-validate by using these features during development
