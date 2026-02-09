# Implementation Plan: Speckle Kanban Board

## Overview

Implement a lightweight web-based kanban board for visualizing beads issues.

**Technology Stack:**
- Python 3.8+ (stdlib only)
- Built-in http.server
- Embedded HTML/CSS (no external files)

## Phases

### Phase 1: Foundation
Core server implementation with basic board rendering.

**Deliverables:**
- `board.py` with HTTP server
- Basic HTML template with 4 columns
- Issue fetching from beads
- Auto-refresh functionality

**Dependencies:** None

### Phase 2: UI Polish  
Card styling and visual refinements.

**Deliverables:**
- Priority color coding (P0-P4)
- Type badges (task, bug, feature, epic)
- Time ago formatting
- Responsive grid layout
- Label display on cards

**Dependencies:** Phase 1

### Phase 3: Command Integration
Claude command and installer integration.

**Deliverables:**
- `speckle.board.md` command definition
- Install.sh updates
- Filter by label feature
- Command-line options (port, refresh, no-browser)

**Dependencies:** Phase 2

### Phase 4: Documentation
User documentation and changelog.

**Deliverables:**
- README.md updates
- CHANGELOG.md entry
- Command help text

**Dependencies:** Phase 3

## Task Breakdown

### Phase 1: Foundation

| Task | Description | Estimate |
|------|-------------|----------|
| T001 | Create board.py with HTTP server skeleton | 15 min |
| T002 | Implement beads JSON fetching | 10 min |
| T003 | Create HTML template with 4-column grid | 20 min |
| T004 | Add auto-refresh meta tag | 5 min |
| T005 | Group issues by status | 10 min |

### Phase 2: UI Polish

| Task | Description | Estimate |
|------|-------------|----------|
| T006 | Add priority color coding to cards | 15 min |
| T007 | Create type badges (task/bug/feature) | 10 min |
| T008 | Implement "time ago" formatting | 10 min |
| T009 | Add responsive CSS grid layout | 15 min |
| T010 | Display labels on cards | 10 min |

### Phase 3: Command Integration

| Task | Description | Estimate |
|------|-------------|----------|
| T011 | Create speckle.board.md command | 15 min |
| T012 | Add CLI argument parsing (port, refresh) | 15 min |
| T013 | Implement label filter dropdown | 20 min |
| T014 | Update install.sh for new files | 10 min |
| T015 | Add browser auto-open with --no-browser flag | 10 min |

### Phase 4: Documentation

| Task | Description | Estimate |
|------|-------------|----------|
| T016 | Update README.md with board command | 15 min |
| T017 | Add CHANGELOG.md entry for v1.2.0 | 10 min |

## Parallel Execution

Tasks that can be executed in parallel:

- **Phase 1:** T001 blocks T002-T005; T002 and T003 can run in parallel after T001
- **Phase 2:** T006, T007, T008, T010 can run in parallel; T009 standalone
- **Phase 3:** T011 and T012 can run in parallel; T013-T015 sequential
- **Phase 4:** T016 and T017 can run in parallel

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Python version incompatibility | Use only stdlib features available in 3.8+ |
| Beads CLI output changes | Graceful error handling, version check |
| Port conflicts | Configurable port, clear error message |
| Browser not opening | Fallback message with URL |

## Definition of Done

- [ ] All tasks completed and tested
- [ ] `/speckle.board` command works end-to-end
- [ ] Board displays correctly in Chrome/Firefox/Safari
- [ ] Auto-refresh works without flicker
- [ ] Filter dropdown works correctly
- [ ] Documentation updated
- [ ] All changes committed and pushed
