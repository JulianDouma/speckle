# Feature Specification: Beads Comments Integration

**Feature Branch**: `001-comments-integration`  
**Created**: 2026-02-09  
**Status**: Draft  
**Input**: User description: "Add beads comments for implementation progress tracking"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record Implementation Progress (Priority: P1)

As an AI agent implementing a task, I want to automatically record what I did as a comment on the bead issue, so that future sessions have context about the implementation.

**Why this priority**: Core value proposition - without comments, there's no memory across sessions.

**Independent Test**: Can be tested by implementing any task and verifying a comment appears on the bead issue with implementation details.

**Acceptance Scenarios**:

1. **Given** a task is being implemented via `/speckle.implement`, **When** the implementation completes successfully, **Then** a comment is added to the bead issue with files changed, lines added/removed, and completion timestamp.

2. **Given** an implementation is in progress, **When** the agent encounters a decision point, **Then** the agent can add a progress note via `/speckle.progress` that's recorded as a comment.

3. **Given** a bead issue has implementation comments, **When** a new session starts, **Then** the agent can read `bd comments <issue-id>` to understand previous work.

---

### User Story 2 - View Implementation History (Priority: P2)

As a developer reviewing past work, I want to see a summary of all implementation activity on a task, so I can understand what was done and why.

**Why this priority**: Complements P1 by making the recorded data useful and accessible.

**Independent Test**: Can be tested by viewing comments on any completed task and verifying the history is coherent and informative.

**Acceptance Scenarios**:

1. **Given** a task with multiple implementation sessions, **When** I run `bd comments <issue-id>`, **Then** I see a chronological list of all progress notes with timestamps.

2. **Given** `/speckle.status` is run, **When** viewing task details, **Then** the most recent progress comment is summarized.

---

### User Story 3 - Manual Progress Notes (Priority: P3)

As an AI agent mid-implementation, I want to record notes about decisions or blockers without completing the task, so that context is preserved if the session ends unexpectedly.

**Why this priority**: Nice-to-have for long-running implementations, but P1/P2 cover the core use case.

**Independent Test**: Can be tested by running `/speckle.progress` with a note and verifying it appears as a bead comment.

**Acceptance Scenarios**:

1. **Given** an implementation is in progress, **When** I run `/speckle.progress "Chose approach X because of Y"`, **Then** a timestamped comment is added to the current task's bead issue.

---

### Edge Cases

- What happens when `bd comments add` fails (beads unavailable)?
  - Log warning but don't fail the implementation
- What happens when no task is currently in progress for `/speckle.progress`?
  - Show error message with guidance to claim a task first
- What happens when comment content is very long (large diff)?
  - Truncate file list to 20 files, summarize total changes

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `/speckle.implement` MUST record a completion comment after successful implementation
- **FR-002**: Completion comments MUST include: files changed, lines added, lines removed, timestamp, actor
- **FR-003**: System MUST provide `/speckle.progress` command for manual progress notes
- **FR-004**: Progress notes MUST be associated with the currently in-progress task
- **FR-005**: Comments MUST be persisted via `bd comments add <issue-id> <content>`
- **FR-006**: Comment failures MUST NOT block implementation workflow (graceful degradation)
- **FR-007**: `/speckle.status` MUST show most recent comment for in-progress tasks

### Key Entities

- **Implementation Comment**: Structured record of work done - includes timestamp, actor, files changed, lines added/removed, optional notes
- **Progress Note**: Freeform text comment with timestamp - for decisions, blockers, or context

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of completed implementations have at least one comment recorded
- **SC-002**: New sessions can retrieve full implementation history in under 2 seconds via `bd comments`
- **SC-003**: `/speckle.progress` adds a comment within 1 second
- **SC-004**: Comment recording failures don't interrupt implementation workflow (0% implementation failures due to comment errors)

## Assumptions

- Beads `bd comments` subcommand is available and functional
- Actor information is available via `BD_ACTOR` env var or `git config user.name`
- Git is available for gathering diff statistics
