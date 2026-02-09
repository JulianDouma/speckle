---
description: Start a lightweight kanban board web server to visualize beads issues
---

# Speckle Board

Launch a local web-based kanban board showing beads issues organized by status.

## Arguments

```text
$ARGUMENTS
```

Options:
- No args: Start on default port 8420
- `--port <number>`: Custom port (default: 8420)
- `--filter <label>`: Filter by label (e.g., "feature:auth", "v0.3.0")
- `--no-browser`: Don't auto-open browser
- `--refresh <seconds>`: Auto-refresh interval (default: 5)

## Examples

```bash
# Basic usage - opens browser automatically
/speckle.board

# Custom port
/speckle.board --port 3000

# Filter to specific feature
/speckle.board --filter "feature:auth"

# Background mode (no browser)
/speckle.board --no-browser

# Slower refresh for large boards
/speckle.board --refresh 10
```

## Prerequisites

```bash
# Check Python is available
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 is required"
    echo "   Install: https://www.python.org/downloads/"
    exit 1
fi

# Check beads is available
if ! command -v bd &>/dev/null; then
    echo "❌ Beads is required"
    echo "   Install: https://github.com/steveyegge/beads"
    exit 1
fi

# Check board.py exists
SCRIPT_PATH=".speckle/scripts/board.py"
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Board script not found: $SCRIPT_PATH"
    echo "   Re-run install.sh to restore missing files"
    exit 1
fi

echo "✅ Prerequisites OK"
```

## Launch Board

```bash
# Default arguments
PORT="8420"
REFRESH="5"
FILTER=""
NO_BROWSER=""

# The board.py script handles all argument parsing
# Pass through all arguments from $ARGUMENTS

echo ""
echo "🔮 Starting Speckle Board..."
echo ""

# Build and execute command
python3 .speckle/scripts/board.py $ARGUMENTS
```

## Features

### Kanban Columns

| Column | Status | Description |
|--------|--------|-------------|
| 📋 BACKLOG | open | Ready to work on |
| 🔄 IN PROGRESS | in_progress | Currently being worked |
| 🚫 BLOCKED | blocked/deferred | Waiting on something |
| ✅ DONE | closed | Completed (last 15) |

### Card Information

Each card shows:
- Issue ID
- Title (truncated to 2 lines)
- Priority indicator (P0-P4 with colors)
- Issue type badge (task/bug/feature/epic)
- Age ("2h ago")
- Labels (up to 3)

### Priority Colors

| Priority | Color | Meaning |
|----------|-------|---------|
| P0-P1 | 🔴 Red | Critical/High |
| P2 | 🟡 Amber | Medium |
| P3-P4 | 🟢 Green | Low |

### Filter by Label

Use the dropdown in the header or `--filter` to focus on specific work:

```bash
# Feature-specific
/speckle.board --filter "feature:auth"

# Version/milestone
/speckle.board --filter "v0.3.0"

# Phase
/speckle.board --filter "phase:mvp"
```

## API Endpoints

The board server also exposes:

| Endpoint | Description |
|----------|-------------|
| `GET /` | HTML board |
| `GET /api/issues` | JSON issue list |
| `GET /health` | Health check |

## Notes

- The board binds to `localhost` only (not accessible from network)
- Auto-refresh polls beads every N seconds
- No write operations - board is read-only
- Closed issues are limited to the last 15
