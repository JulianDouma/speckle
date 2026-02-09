---
description: Add a manual progress note to the current in-progress task
---

# Speckle Progress

Add a manual progress note to the currently in-progress task. Useful for recording decisions, blockers, or context mid-implementation.

## Arguments

```text
$ARGUMENTS
```

The text after `/speckle.progress` becomes the progress note content.

Example: `/speckle.progress "Chose JWT over sessions for stateless auth"`

## Prerequisites

```bash
# Source comment helpers
source ".speckle/scripts/comments.sh"

# Verify beads is available
if ! command -v bd &>/dev/null; then
    echo "❌ Beads not installed"
    exit 1
fi
```

## Find Current Task

```bash
# Look for in-progress tasks
IN_PROGRESS=$(bd list --status in_progress 2>/dev/null | grep "speckle-" || echo "")

if [ -z "$IN_PROGRESS" ]; then
    echo "❌ No task currently in progress"
    echo ""
    echo "To start a task, run:"
    echo "   /speckle.implement"
    echo ""
    echo "Or claim a specific task:"
    echo "   bd update <issue-id> --status in_progress"
    exit 1
fi

# Extract the first in-progress issue ID
CURRENT_ISSUE=$(echo "$IN_PROGRESS" | head -1 | grep -oE 'speckle-[a-z0-9]+')
CURRENT_TITLE=$(echo "$IN_PROGRESS" | head -1 | sed 's/.*speckle-[a-z0-9]*: //')

echo "📋 Current task: $CURRENT_ISSUE"
echo "   $CURRENT_TITLE"
```

## Validate Note Content

```bash
NOTE="$ARGUMENTS"

if [ -z "$NOTE" ]; then
    echo ""
    echo "❌ No note provided"
    echo ""
    echo "Usage: /speckle.progress \"your progress note here\""
    echo ""
    echo "Examples:"
    echo "   /speckle.progress \"Decided to use Redis for caching\""
    echo "   /speckle.progress \"Blocked: waiting for API access\""
    echo "   /speckle.progress \"Refactored to use strategy pattern\""
    exit 1
fi
```

## Extract Task ID (if available)

```bash
# Try to extract task ID from the issue title (e.g., "T001: description")
TASK_ID=$(echo "$CURRENT_TITLE" | grep -oE '^T[0-9]{3}' || echo "")
```

## Record Progress Note

```bash
echo ""
echo "📝 Recording progress note..."

# Format the progress note
COMMENT=$(format_progress_note "$NOTE" "$TASK_ID" "$CURRENT_ISSUE")

# Add comment safely
if add_comment_safe "$CURRENT_ISSUE" "$COMMENT"; then
    echo ""
    echo "✅ Progress note recorded"
    echo ""
    echo "View all comments:"
    echo "   bd comments $CURRENT_ISSUE"
else
    echo ""
    echo "⚠️  Could not record note to beads"
    echo "   Note content preserved above for manual recording"
fi
```

## Show Recent Activity

```bash
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📜 Recent Activity on $CURRENT_ISSUE"
echo "═══════════════════════════════════════════════════════════"

# Show last few comments
bd comments "$CURRENT_ISSUE" 2>/dev/null | tail -10 || echo "(no comments yet)"
```
