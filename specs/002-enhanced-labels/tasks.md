# Tasks: Enhanced Labels

**Input**: Design documents from `/specs/002-enhanced-labels/`

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Foundation

**Purpose**: Create label generation helper functions

- [ ] T001 Create `.speckle/scripts/labels.sh` with slugify function
- [ ] T002 [P] Add `extract_phase_label()` function to labels.sh
- [ ] T003 [P] Add `extract_story_label()` function to labels.sh
- [ ] T004 Add `build_label_string()` function to labels.sh

---

## Phase 2: User Story 1 - Automatic Label Generation (Priority: P1) 🎯 MVP

**Goal**: Sync tasks with rich labels automatically

### Implementation for User Story 1

- [ ] T005 [US1] Update `speckle.sync.md` to source labels.sh
- [ ] T006 [US1] Add feature label generation from branch name
- [ ] T007 [US1] Add phase label generation from markdown headers
- [ ] T008 [US1] Add story/parallel label generation from markers
- [ ] T009 [US1] Pass labels to `bd create --labels`

**Checkpoint**: Synced tasks have rich labels

---

## Phase 3: User Story 2 - Filter by Labels (Priority: P2)

**Goal**: Verify label filtering works with beads

### Implementation for User Story 2

- [ ] T010 [US2] Test `bd list --label` filtering (verify beads support)
- [ ] T011 [US2] Document label filtering in README

---

## Phase 4: User Story 3 - Status Enhancement (Priority: P3)

**Goal**: Show progress by phase in status command

### Implementation for User Story 3

- [ ] T012 [US3] Update `speckle.status.md` to group by phase
- [ ] T013 [US3] Add per-phase completion percentages
- [ ] T014 [US3] Add `--by-story` option for story breakdown

---

## Phase 5: Polish

- [ ] T015 [P] Update SELF-HOSTING.md with v0.3.0 entry
- [ ] T016 Self-validate: Check own issues have labels

---

## Dependencies

- T002, T003 can run in parallel (different functions)
- T005-T009 are sequential (building same feature)
- T012-T014 are sequential (building same command)
