# Tasks: Speckle Kanban Board

## Phase 1: Foundation

### T001: Create board.py HTTP server skeleton
- [ ] Create `.speckle/scripts/board.py`
- [ ] Import http.server, json, subprocess, argparse
- [ ] Create BoardHandler class extending BaseHTTPRequestHandler
- [ ] Implement do_GET for `/` and `/health` endpoints
- [ ] Add main() with argument parsing
- [ ] Test server starts and responds

**Labels:** phase:foundation

### T002: Implement beads JSON fetching
- [ ] Create get_issues() function
- [ ] Execute `bd list --all --json` subprocess
- [ ] Parse JSON response
- [ ] Handle errors gracefully (empty list on failure)
- [ ] Add timeout handling

**Labels:** phase:foundation, parallel

### T003: Create HTML template with 4-column grid
- [ ] Create HTML_TEMPLATE constant with embedded CSS
- [ ] Define CSS Grid layout for 4 columns
- [ ] Create column containers (backlog, in_progress, blocked, closed)
- [ ] Add header with title
- [ ] Add footer with timestamp

**Labels:** phase:foundation, parallel

### T004: Add auto-refresh functionality
- [ ] Add meta refresh tag with configurable interval
- [ ] Display refresh indicator in header
- [ ] Pass refresh interval to template

**Labels:** phase:foundation

### T005: Group issues by status
- [ ] Create group_by_status() function
- [ ] Map statuses to columns (deferred → blocked)
- [ ] Sort by priority within columns
- [ ] Limit closed issues to last 15

**Labels:** phase:foundation

---

## Phase 2: UI Polish

### T006: Add priority color coding
- [ ] Define CSS variables for P0-P4 colors
- [ ] Add priority class to card element
- [ ] Style left border based on priority
- [ ] Add priority badge in card header

**Labels:** phase:polish, parallel

### T007: Create type badges
- [ ] Add type badge element to card template
- [ ] Style badges for task, bug, feature, epic
- [ ] Use distinct colors for each type

**Labels:** phase:polish, parallel

### T008: Implement time ago formatting
- [ ] Create time_ago() function
- [ ] Parse ISO timestamps
- [ ] Return human-readable format (2h ago, 3d ago)
- [ ] Handle edge cases (just now, weeks)

**Labels:** phase:polish, parallel

### T009: Add responsive CSS grid layout
- [ ] Set max-width for board container
- [ ] Add media queries for tablet (2 columns)
- [ ] Add media queries for mobile (1 column)
- [ ] Ensure cards stack properly

**Labels:** phase:polish

### T010: Display labels on cards
- [ ] Add labels container to card template
- [ ] Render up to 3 labels per card
- [ ] Style as small chips
- [ ] Filter out internal labels (speckle-)

**Labels:** phase:polish, parallel

---

## Phase 3: Command Integration

### T011: Create speckle.board.md command
- [ ] Create `.claude/commands/speckle.board.md`
- [ ] Add description and arguments section
- [ ] Document all options
- [ ] Add usage examples
- [ ] Add prerequisites check

**Labels:** phase:integration, parallel

### T012: Add CLI argument parsing
- [ ] Add --port argument (default: 8420)
- [ ] Add --refresh argument (default: 5)
- [ ] Add --no-browser flag
- [ ] Add --filter argument
- [ ] Print startup banner with settings

**Labels:** phase:integration, parallel

### T013: Implement label filter dropdown
- [ ] Extract unique labels from issues
- [ ] Create filter select element in header
- [ ] Handle filter via query parameter
- [ ] Preserve filter across refreshes
- [ ] Add "All issues" option

**Labels:** phase:integration

### T014: Update install.sh for new files
- [ ] Add board.py to scripts installation
- [ ] Add speckle.board.md to commands installation
- [ ] Add to uninstall list
- [ ] Add to available commands output

**Labels:** phase:integration

### T015: Add browser auto-open
- [ ] Import webbrowser module
- [ ] Open URL after server starts
- [ ] Respect --no-browser flag
- [ ] Handle webbrowser errors gracefully

**Labels:** phase:integration

---

## Phase 4: Documentation

### T016: Update README.md
- [ ] Add /speckle.board to commands table
- [ ] Add Board section with screenshot placeholder
- [ ] Document usage and options
- [ ] Add troubleshooting tips

**Labels:** phase:docs, parallel

### T017: Update CHANGELOG.md
- [ ] Add v1.2.0 section
- [ ] Document new /speckle.board command
- [ ] List all features (columns, cards, filter, refresh)
- [ ] Reference issue number

**Labels:** phase:docs, parallel
