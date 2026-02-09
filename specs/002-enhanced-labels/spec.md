# Feature Specification: Enhanced Labels

**Feature Branch**: `002-enhanced-labels`  
**Created**: 2026-02-09  
**Status**: Draft  
**Input**: User description: "Add rich labeling to synced tasks for better filtering and organization"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automatic Label Generation (Priority: P1)

As a developer using Speckle sync, I want tasks to automatically receive rich labels based on their context, so I can filter and organize work effectively using beads.

**Why this priority**: Core value - without labels, beads filtering is limited to title/description search.

**Independent Test**: Sync tasks.md and verify bead issues have appropriate labels.

**Acceptance Scenarios**:

1. **Given** a task in Phase "Setup", **When** synced, **Then** bead issue has label `phase:setup`
2. **Given** a task with `[US2]` marker, **When** synced, **Then** bead issue has label `story:us2`
3. **Given** a task with `[P]` marker, **When** synced, **Then** bead issue has label `parallel`
4. **Given** a task in a feature branch `001-comments-integration`, **When** synced, **Then** bead issue has label `feature:001-comments-integration`

---

### User Story 2 - Filter by Labels (Priority: P2)

As a developer reviewing work, I want to filter tasks by label, so I can focus on specific phases or stories.

**Why this priority**: Builds on US1 to make labels useful.

**Independent Test**: Use `bd list --label <label>` to filter issues.

**Acceptance Scenarios**:

1. **Given** tasks with various labels, **When** I run `bd list --label story:us1`, **Then** only US1 tasks are shown
2. **Given** parallel tasks labeled, **When** I run `bd list --label parallel`, **Then** all parallelizable tasks shown

---

### User Story 3 - Label Summary in Status (Priority: P3)

As a developer checking progress, I want `/speckle.status` to show progress by label groups, so I can see phase/story completion rates.

**Why this priority**: Enhancement to status command leveraging labels.

**Independent Test**: Run `/speckle.status` and see breakdown by phase.

**Acceptance Scenarios**:

1. **Given** tasks with phase labels, **When** running `/speckle.status`, **Then** shows completion % per phase
2. **Given** tasks with story labels, **When** running `/speckle.status --by-story`, **Then** shows completion % per story

---

### Edge Cases

- What if task has no clear phase (not under a phase header)?
  - Use `phase:unassigned` label
- What if phase name has special characters?
  - Slugify to lowercase alphanumeric with hyphens
- What if labels exceed beads limit?
  - Prioritize: feature > phase > story > parallel

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `/speckle.sync` MUST generate `feature:<branch>` label for all synced tasks
- **FR-002**: `/speckle.sync` MUST generate `phase:<name>` label based on markdown headers
- **FR-003**: `/speckle.sync` MUST generate `story:<id>` label from `[US#]` markers
- **FR-004**: `/speckle.sync` MUST generate `parallel` label from `[P]` markers
- **FR-005**: All label values MUST be slugified (lowercase, hyphens, no special chars)
- **FR-006**: `/speckle.status` MUST show progress breakdown by phase labels
- **FR-007**: Label generation MUST be idempotent (re-sync doesn't duplicate labels)

### Key Entities

- **Label**: Key-value pair attached to bead issues (e.g., `phase:setup`, `story:us1`)
- **Label Group**: Category prefix for filtering (e.g., `phase:`, `story:`, `feature:`)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of synced tasks have at least a `feature:` label
- **SC-002**: Tasks under phase headers have `phase:` labels with 100% accuracy
- **SC-003**: `bd list --label` filtering works for all generated label types
- **SC-004**: `/speckle.status` shows phase breakdown when labels present

## Assumptions

- Beads supports `--labels` flag on `bd create` (verified in v0.2.0)
- Beads supports `--label` flag on `bd list` for filtering
- Phase names are extracted from markdown `##` or `###` headers
