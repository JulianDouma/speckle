---
description: Review and prioritize issues across GitHub and beads
---

# Speckle Triage

Review, prioritize, and sync issues between GitHub and beads.

## Arguments

```text
$ARGUMENTS
```

**Options**:
| Option | Description |
|--------|-------------|
| (none) | Show triage dashboard overview |
| `--sync` | Sync all open GitHub issues to beads |
| `--stale` | Find stale issues that need attention |
| `--priority <id> <0-4>` | Set priority for specific issue |
| `--labels <id> <labels>` | Add labels to specific issue |
| `--start <id>` | Start work on issue (set in_progress) |
| `--block <id> <reason>` | Block issue with reason |
| `--close <id>` | Close issue |
| `--list` | List issues needing triage (no priority set) |

**Examples**:
```bash
# View dashboard
/speckle.triage

# Sync GitHub issues
/speckle.triage --sync

# Set priority
/speckle.triage --priority speckle-abc 1

# Start work
/speckle.triage --start speckle-xyz

# Find stale issues
/speckle.triage --stale
```

**Note**: The old `--review` interactive mode is deprecated. Use specific actions instead.

## Prerequisites

```bash
# Source common utilities
source ".speckle/scripts/common.sh"

# Check GitHub CLI is available
if ! command -v gh &> /dev/null; then
    log_error "GitHub CLI not installed"
    echo "Install from: https://cli.github.com"
    exit 1
fi

# Check beads is available
if ! check_beads; then
    exit 1
fi

# Verify gh is authenticated
if ! gh auth status &>/dev/null; then
    log_error "GitHub CLI not authenticated"
    echo "Run: gh auth login"
    exit 1
fi
```

## Parse Arguments

```bash
ARGS="$ARGUMENTS"
ACTION=""
TARGET_ID=""
ACTION_VALUE=""

# Parse arguments
if [[ "$ARGS" == *"--sync"* ]]; then
    ACTION="sync"
elif [[ "$ARGS" == *"--stale"* ]]; then
    ACTION="stale"
elif [[ "$ARGS" == *"--list"* ]]; then
    ACTION="list"
elif [[ "$ARGS" =~ --priority[[:space:]]+([a-z0-9-]+)[[:space:]]+([0-4]) ]]; then
    ACTION="priority"
    TARGET_ID="${BASH_REMATCH[1]}"
    ACTION_VALUE="${BASH_REMATCH[2]}"
elif [[ "$ARGS" =~ --labels[[:space:]]+([a-z0-9-]+)[[:space:]]+(.+) ]]; then
    ACTION="labels"
    TARGET_ID="${BASH_REMATCH[1]}"
    ACTION_VALUE="${BASH_REMATCH[2]}"
elif [[ "$ARGS" =~ --start[[:space:]]+([a-z0-9-]+) ]]; then
    ACTION="start"
    TARGET_ID="${BASH_REMATCH[1]}"
elif [[ "$ARGS" =~ --block[[:space:]]+([a-z0-9-]+)[[:space:]]+(.+) ]]; then
    ACTION="block"
    TARGET_ID="${BASH_REMATCH[1]}"
    ACTION_VALUE="${BASH_REMATCH[2]}"
elif [[ "$ARGS" =~ --close[[:space:]]+([a-z0-9-]+) ]]; then
    ACTION="close"
    TARGET_ID="${BASH_REMATCH[1]}"
elif [[ "$ARGS" == *"--review"* ]]; then
    echo "⚠️  --review (interactive mode) is deprecated"
    echo ""
    echo "Use specific actions instead:"
    echo "  /speckle.triage --priority <id> <0-4>"
    echo "  /speckle.triage --labels <id> <labels>"
    echo "  /speckle.triage --start <id>"
    echo "  /speckle.triage --block <id> <reason>"
    echo "  /speckle.triage --close <id>"
    echo "  /speckle.triage --list"
    exit 1
else
    # Default: show dashboard
    ACTION="dashboard"
fi
```

## Batch Actions

```bash
# Handle single-issue batch actions
case "$ACTION" in
    priority)
        bd update "$TARGET_ID" --priority "$ACTION_VALUE"
        log_success "Priority set to P$ACTION_VALUE for $TARGET_ID"
        exit 0
        ;;
    labels)
        bd update "$TARGET_ID" --labels "$ACTION_VALUE"
        log_success "Labels added to $TARGET_ID"
        exit 0
        ;;
    start)
        bd update "$TARGET_ID" --status in_progress
        log_success "Started work on $TARGET_ID"
        exit 0
        ;;
    block)
        bd update "$TARGET_ID" --status blocked
        bd comment "$TARGET_ID" "Blocked: $ACTION_VALUE" 2>/dev/null || true
        log_success "Blocked $TARGET_ID: $ACTION_VALUE"
        exit 0
        ;;
    close)
        bd close "$TARGET_ID"
        log_success "Closed $TARGET_ID"
        exit 0
        ;;
    list)
        echo "📋 Issues needing triage"
        echo "════════════════════════════════════════════════════════════"
        echo ""
        bd list --status open 2>/dev/null | head -30
        echo ""
        echo "Use: /speckle.triage --priority <id> <0-4> to set priorities"
        exit 0
        ;;
esac
```

## Dashboard View

```bash
if [ "$ACTION" = "dashboard" ]; then
    echo "📊 Speckle Issue Triage Dashboard"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    
    # Get GitHub issues count
    GH_OPEN=$(gh issue list --state open --json number --jq 'length' 2>/dev/null || echo "0")
    GH_BUGS=$(gh issue list --state open --label bug --json number --jq 'length' 2>/dev/null || echo "0")
    GH_FEATURES=$(gh issue list --state open --label feature --json number --jq 'length' 2>/dev/null || echo "0")
    
    # Get beads counts
    BD_OPEN=$(bd list --status open 2>/dev/null | wc -l | tr -d ' ')
    BD_IN_PROGRESS=$(bd list --status in_progress 2>/dev/null | wc -l | tr -d ' ')
    BD_BLOCKED=$(bd list --status blocked 2>/dev/null | wc -l | tr -d ' ')
    
    echo "📌 GitHub Issues"
    echo "   Open: $GH_OPEN"
    echo "   Bugs: $GH_BUGS"
    echo "   Features: $GH_FEATURES"
    echo ""
    echo "🔮 Beads Issues"
    echo "   Open: $BD_OPEN"
    echo "   In Progress: $BD_IN_PROGRESS"
    echo "   Blocked: $BD_BLOCKED"
    echo ""
    
    # Check for sync issues
    echo "⚠️  Potential Issues:"
    
    # Find GitHub issues not in beads
    UNSYNCED=0
    while IFS= read -r issue; do
        GH_NUM=$(echo "$issue" | jq -r '.number')
        # Check if beads has this issue
        if ! bd list 2>/dev/null | grep -q "gh-$GH_NUM"; then
            UNSYNCED=$((UNSYNCED + 1))
        fi
    done < <(gh issue list --state open --json number 2>/dev/null)
    
    if [ "$UNSYNCED" -gt 0 ]; then
        echo "   $UNSYNCED GitHub issue(s) not synced to beads"
        echo "   Run: /speckle.triage --sync"
    else
        echo "   None - all issues synced!"
    fi
    
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Actions:"
    echo "  /speckle.triage --sync    Sync GitHub issues to beads"
    echo "  /speckle.triage --review  Interactive issue review"
    echo "  /speckle.triage --stale   Find stale issues"
    
    exit 0
fi
```

## Sync Action

```bash
if [ "$ACTION" = "sync" ]; then
    echo "🔄 Syncing GitHub Issues to Beads"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    
    SYNCED=0
    SKIPPED=0
    
    # Get all open GitHub issues
    gh issue list --state open --json number,title,labels,body --limit 100 2>/dev/null | jq -c '.[]' | while read -r issue; do
        GH_NUM=$(echo "$issue" | jq -r '.number')
        GH_TITLE=$(echo "$issue" | jq -r '.title')
        GH_LABELS=$(echo "$issue" | jq -r '.labels[].name' | tr '\n' ',' | sed 's/,$//')
        
        # Check if already synced
        if bd list 2>/dev/null | grep -q "gh-$GH_NUM"; then
            echo "⏭️  #$GH_NUM - Already synced"
            continue
        fi
        
        # Determine type from labels
        BD_TYPE="task"
        if echo "$GH_LABELS" | grep -qi "bug"; then
            BD_TYPE="bug"
        elif echo "$GH_LABELS" | grep -qi "feature"; then
            BD_TYPE="feature"
        fi
        
        # Determine priority from labels
        PRIORITY=2
        if echo "$GH_LABELS" | grep -qi "critical\|p0"; then
            PRIORITY=0
        elif echo "$GH_LABELS" | grep -qi "high\|p1"; then
            PRIORITY=1
        elif echo "$GH_LABELS" | grep -qi "low\|p3\|p4"; then
            PRIORITY=3
        fi
        
        # Create beads issue
        BD_ID=$(bd create "$GH_TITLE" \
            --type "$BD_TYPE" \
            --priority "$PRIORITY" \
            --labels "speckle,gh-$GH_NUM,$GH_LABELS" \
            --description "Synced from GitHub Issue #$GH_NUM

https://github.com/$(gh repo view --json nameWithOwner --jq '.nameWithOwner')/issues/$GH_NUM

---
*Synced by Speckle triage*" 2>&1 | grep -oE 'speckle-[a-z0-9]+')
        
        if [ -n "$BD_ID" ]; then
            echo "✅ #$GH_NUM -> $BD_ID: $GH_TITLE"
            SYNCED=$((SYNCED + 1))
        else
            echo "❌ #$GH_NUM - Failed to sync"
        fi
    done
    
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "✅ Sync complete"
    echo ""
    echo "Run \`bd ready\` to see available work"
    
    exit 0
fi
```

## Stale Action

```bash
if [ "$ACTION" = "stale" ]; then
    echo "🕸️  Stale Issue Detection"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    
    # Define stale threshold (14 days)
    STALE_DAYS=14
    STALE_THRESHOLD=$(date -v-${STALE_DAYS}d +%Y-%m-%d 2>/dev/null || date -d "$STALE_DAYS days ago" +%Y-%m-%d 2>/dev/null || echo "2026-01-26")
    
    echo "Finding issues not updated since $STALE_THRESHOLD..."
    echo ""
    
    # Check GitHub issues
    echo "📌 Stale GitHub Issues:"
    STALE_GH=$(gh issue list --state open --json number,title,updatedAt --jq ".[] | select(.updatedAt < \"${STALE_THRESHOLD}T00:00:00Z\") | \"  #\(.number) - \(.title)\"" 2>/dev/null)
    
    if [ -n "$STALE_GH" ]; then
        echo "$STALE_GH"
    else
        echo "  None found"
    fi
    
    echo ""
    echo "🔮 Stale Beads Issues (in_progress for too long):"
    
    # Get in_progress issues (beads doesn't have date filtering, so we list and check)
    bd list --status in_progress 2>/dev/null | while read -r line; do
        ISSUE_ID=$(echo "$line" | awk '{print $1}')
        if [ -n "$ISSUE_ID" ]; then
            echo "  $ISSUE_ID - Consider reviewing progress"
        fi
    done
    
    echo ""
    echo "🔮 Blocked Issues:"
    bd list --status blocked 2>/dev/null | while read -r line; do
        ISSUE_ID=$(echo "$line" | awk '{print $1}')
        if [ -n "$ISSUE_ID" ]; then
            TITLE=$(bd show "$ISSUE_ID" 2>/dev/null | grep -m1 "title:" | cut -d: -f2- | xargs)
            echo "  $ISSUE_ID - $TITLE"
        fi
    done
    
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Recommendations:"
    echo "  - Review stale issues and close or update them"
    echo "  - Check blocked issues for unblocking opportunities"
    echo "  - Use /speckle.triage --review for interactive triage"
    
    exit 0
fi
```
