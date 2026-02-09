# Tasks: Epic Lifecycle

**Input**: Design documents from `/specs/003-epic-lifecycle/`

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Foundation

**Purpose**: Create epic management helper functions

- [ ] T001 Create `.speckle/scripts/epics.sh` skeleton
- [ ] T002 [P] Add `create_epic()` function
- [ ] T003 [P] Add `get_epic_id()` function
- [ ] T004 Add `update_epic_status()` function
- [ ] T005 Add `get_epic_progress()` function

---

## Phase 2: User Story 1 - Epic Creation (Priority: P1) 🎯 MVP

**Goal**: Auto-create epic when syncing feature

### Implementation for User Story 1

- [ ] T006 [US1] Update speckle.sync.md to source epics.sh
- [ ] T007 [US1] Add epic creation logic to sync
- [ ] T008 [US1] Store epicId in mapping file
- [ ] T009 [US1] Link tasks to epic via bd dep add

**Checkpoint**: Syncing creates epic with linked tasks

---

## Phase 3: User Story 2 - State Transitions (Priority: P2)

**Goal**: Epic status reflects task states

### Implementation for User Story 2

- [ ] T010 [US2] Implement state transition logic in update_epic_status()
- [ ] T011 [US2] Call status update after task sync
- [ ] T012 [US2] Handle edge cases (manual changes, inconsistencies)

---

## Phase 4: User Story 3 - Progress Display (Priority: P3)

**Goal**: Show epic in status command

### Implementation for User Story 3

- [ ] T013 [US3] Update speckle.status.md to show epic summary
- [ ] T014 [US3] Add epic progress bar visualization
- [ ] T015 [US3] Add --epics option for multi-epic view

---

## Phase 5: Polish

- [ ] T016 [P] Update SELF-HOSTING.md with v0.4.0 entry
- [ ] T017 Self-validate: Check own feature has epic

---

## Dependencies

- T002, T003 can run in parallel
- T006-T009 are sequential (building sync feature)
- T010-T012 depend on US1 completion
- T013-T015 are sequential (building status feature)
