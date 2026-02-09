# Feature Specification: Epic Lifecycle

**Feature Branch**: `003-epic-lifecycle`  
**Created**: 2026-02-09  
**Status**: Draft  
**Input**: "Track features as epics with lifecycle states and progress aggregation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Epic Creation (Priority: P1)

As a developer starting a new feature, I want an epic issue created automatically when I sync, so all tasks are grouped under a parent issue.

**Why this priority**: Foundation for epic tracking - without the epic, no lifecycle.

**Independent Test**: Run `/speckle.sync` on a new feature and verify epic issue created.

**Acceptance Scenarios**:

1. **Given** a new feature with tasks.md, **When** `/speckle.sync` runs, **Then** an epic issue is created with type=epic
2. **Given** an epic exists, **When** tasks are synced, **Then** tasks are linked to the epic via `bd dep add`
3. **Given** an epic, **When** viewing with `bd show`, **Then** epic description includes feature summary from spec.md

---

### User Story 2 - Epic State Transitions (Priority: P2)

As a developer working on a feature, I want the epic status to reflect the feature's lifecycle stage, so stakeholders can see progress at a glance.

**Why this priority**: Makes epics useful for tracking, builds on US1.

**Independent Test**: Complete tasks and verify epic status updates.

**Acceptance Scenarios**:

1. **Given** a new epic, **When** no tasks started, **Then** epic status is `open` (draft)
2. **Given** an epic, **When** first task moves to in_progress, **Then** epic status becomes `in_progress`
3. **Given** an epic, **When** all tasks closed, **Then** epic status becomes `closed`

---

### User Story 3 - Epic Progress Display (Priority: P3)

As a developer checking status, I want `/speckle.status` to show epic-level progress, so I can see the big picture.

**Why this priority**: Visualization of epic progress, builds on US1/US2.

**Independent Test**: Run `/speckle.status` and see epic summary.

**Acceptance Scenarios**:

1. **Given** an active epic, **When** running `/speckle.status`, **Then** shows epic name, status, and task completion percentage
2. **Given** multiple epics, **When** running `/speckle.status --epics`, **Then** shows all epics with their progress

---

### Edge Cases

- What if epic already exists when syncing?
  - Update epic description, don't create duplicate
- What if tasks are manually closed outside of Speckle?
  - Epic status should still reflect reality on next sync
- What if epic is manually closed but tasks remain?
  - Warn user about inconsistency

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `/speckle.sync` MUST create epic issue if not exists for feature
- **FR-002**: Epic MUST have type=epic and label `epic:<feature-name>`
- **FR-003**: Task issues MUST be linked to epic via dependency
- **FR-004**: Epic status MUST transition based on task states
- **FR-005**: `/speckle.status` MUST show epic summary with progress
- **FR-006**: Epic description MUST include summary from spec.md
- **FR-007**: Mapping file MUST track epic ID: `{"epicId": "speckle-xxx", ...}`

### Key Entities

- **Epic**: Parent issue representing a feature (type=epic)
- **Epic State**: open (draft) → in_progress → closed
- **Epic Progress**: Percentage of linked tasks that are closed

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of synced features have an epic issue
- **SC-002**: Epic status reflects actual task states with 100% accuracy
- **SC-003**: `/speckle.status` shows epic progress within 1 second
- **SC-004**: Epic transitions happen automatically on sync

## Assumptions

- Beads supports `--type epic` for issue creation
- Beads supports linking issues via `bd dep add`
- Can query tasks linked to an epic via labels or dependencies
