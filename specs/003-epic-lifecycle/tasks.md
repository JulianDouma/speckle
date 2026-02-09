# Tasks: Epic Lifecycle

**Input**: Design documents from `/specs/003-epic-lifecycle/`

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Foundation

**Purpose**: Create epic management helper functions

- [x] T001 Create `.speckle/scripts/epics.sh` skeleton
- [x] T002 [P] Add `create_epic()` function
- [x] T003 [P] Add `get_epic_id()` function
- [x] T004 Add `update_epic_status()` function
- [x] T005 Add `get_epic_progress()` function

---

## Phase 2: User Story 1 - Epic Creation (Priority: P1) 🎯 MVP

**Goal**: Auto-create epic when syncing feature

### Implementation for User Story 1

- [x] T006 [US1] Update speckle.sync.md to source epics.sh
- [x] T007 [US1] Add epic creation logic to sync
- [x] T008 [US1] Store epicId in mapping file
- [x] T009 [US1] Link tasks to epic via bd dep add

**Checkpoint**: Syncing creates epic with linked tasks

---

## Phase 3: User Story 2 - State Transitions (Priority: P2)

**Goal**: Epic status reflects task states

### Implementation for User Story 2

- [x] T010 [US2] Implement state transition logic in update_epic_status()
- [x] T011 [US2] Call status update after task sync
- [x] T012 [US2] Handle edge cases (manual changes, inconsistencies)

---

## Phase 4: User Story 3 - Progress Display (Priority: P3)

**Goal**: Show epic in status command

### Implementation for User Story 3

- [x] T013 [US3] Update speckle.status.md to show epic summary
- [x] T014 [US3] Add epic progress bar visualization
- [x] T015 [US3] Add --epics option for multi-epic view

---

## Phase 5: Polish

- [x] T016 [P] Update SELF-HOSTING.md with v0.4.0 entry
- [x] T017 Self-validate: Check own feature has epic

---

## Dependencies

- T002, T003 can run in parallel
- T006-T009 are sequential (building sync feature)
- T010-T012 depend on US1 completion
- T013-T015 are sequential (building status feature)
