# Speckle Kanban Board

## Problem Statement

During development sessions, developers need a quick visual overview of their beads issues organized by status. Currently, they must use CLI commands (`bd list`, `bd status`) which provide text output that's harder to scan visually. A lightweight web-based kanban board would provide:

1. **At-a-glance status** - See all work organized by status columns
2. **Priority visibility** - Quickly identify high-priority items
3. **Session continuity** - Keep a browser tab open during development
4. **Low friction** - Start instantly with zero configuration

## Goals

- Provide a lightweight, web-based kanban visualization of beads issues
- Expose via local port for browser access
- Auto-refresh to stay current during development
- Display useful information without overwhelming
- Zero external dependencies (Python stdlib only)

## Non-Goals

- Full project management features (drag-drop, editing)
- Multi-user collaboration
- Persistent state or database
- Complex filtering/sorting UI
- Mobile-first design

## User Stories

### US1: View Kanban Board
As a developer, I want to view my beads issues in a kanban board layout so that I can quickly see the status of all work.

**Acceptance Criteria:**
- Board displays 4 columns: Backlog, In Progress, Blocked, Done
- Issues are grouped by their beads status
- Each card shows issue ID, title, priority, and type
- Board is accessible via web browser

### US2: Start Board Server
As a developer, I want to start the kanban board server with a simple command so that I can quickly visualize my work.

**Acceptance Criteria:**
- `/speckle.board` command starts the server
- Server binds to localhost on configurable port (default: 8420)
- Browser opens automatically (can be disabled)
- Clear output shows URL and how to stop

### US3: Auto-Refresh Board
As a developer, I want the board to automatically refresh so that I see current data without manual intervention.

**Acceptance Criteria:**
- Board auto-refreshes at configurable interval (default: 5s)
- Refresh indicator shows countdown
- No flicker or scroll position loss on refresh

### US4: Filter by Label
As a developer, I want to filter the board by label so that I can focus on specific work.

**Acceptance Criteria:**
- Dropdown shows all available labels
- Selecting a label filters all columns
- Filter persists across refreshes
- Can clear filter to show all

## Technical Design

### Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   bd list   │────▶│  board.py   │────▶│   Browser   │
│   --json    │     │  (Python)   │     │  (HTML/CSS) │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Technology Choice

**Python http.server** - Zero external dependencies, Python already required for spec-kit.

### File Structure

```
.speckle/scripts/board.py      # Server implementation
.claude/commands/speckle.board.md  # Command definition
```

### Data Flow

1. Command invokes `python3 .speckle/scripts/board.py`
2. Server fetches issues via `bd list --json`
3. Groups issues by status into columns
4. Renders HTML with embedded CSS
5. Browser auto-refreshes via meta tag

### Card Design

```
┌─────────────────────────┐
│ 🔴 speckle-abc          │  ← Priority color + ID
│ ─────────────────────── │
│ Create login form for   │  ← Title (max 2 lines)
│ user authentication     │
│ ─────────────────────── │
│ [task] • 2h ago         │  ← Type + Age
└─────────────────────────┘
```

### Column Layout

| Column | Status | Color |
|--------|--------|-------|
| Backlog | open | Light gray |
| In Progress | in_progress | Light blue |
| Blocked | blocked, deferred | Light red |
| Done | closed | Light green |

## Constraints

- Must work with Python 3.8+ (stdlib only)
- Must bind to localhost only (security)
- Must be read-only (no write operations)
- Must handle empty/missing beads gracefully
- Server must be single-threaded (simplicity)

## Success Metrics

- Server starts in < 1 second
- Page loads in < 200ms
- Memory usage < 50MB
- Works on macOS and Linux
