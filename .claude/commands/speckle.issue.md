---
description: Create a GitHub issue using a guided, spec-driven workflow
---

# Speckle Issue

Guided issue creation that integrates with beads tracking and optionally links to specs.

## Arguments

```text
$ARGUMENTS
```

**Usage**: `/speckle.issue "<title>" [--type <type>] [--priority <0-4>] [--labels <labels>] [--spec <name>]`

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `<title>` | Yes | - | Issue title (quoted string) |
| `--type` | No | feature | One of: feature, bug, enhancement, chore, docs |
| `--priority` | No | 2 | Priority 0-4 (0=critical, 4=low) |
| `--labels` | No | - | Comma-separated labels |
| `--spec` | No | - | Spec name to link (e.g., "001-feature-name") |
| `--description` | No | - | Issue description |

**Examples**:
```bash
# Simple feature
/speckle.issue "Add dark mode support"

# Bug with priority
/speckle.issue "Login fails on Safari" --type bug --priority 1

# Feature linked to spec
/speckle.issue "User comments system" --type feature --spec 001-comments

# Full specification
/speckle.issue "API rate limiting" --type feature --priority 1 --labels "api,security" --description "Implement rate limiting for all API endpoints"
```

**Note**: If called without arguments, Claude will ask for the required information interactively.

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

## Parse Input

```bash
# Parse arguments - supports both positional and named arguments
# Format: "<title>" [--type <type>] [--priority <0-4>] [--labels <labels>] [--spec <name>] [--description <desc>]

ISSUE_TITLE=""
ISSUE_TYPE="feature"
PRIORITY=2
EXTRA_LABELS=""
SPEC_LINK=""
DESCRIPTION=""
CREATE_SPEC=false

# Parse arguments
ARGS="$ARGUMENTS"
while [[ -n "$ARGS" ]]; do
    case "$ARGS" in
        --type*)
            ARGS="${ARGS#--type}"
            ARGS="${ARGS# }"
            ISSUE_TYPE="${ARGS%% *}"
            ARGS="${ARGS#$ISSUE_TYPE}"
            ;;
        --priority*)
            ARGS="${ARGS#--priority}"
            ARGS="${ARGS# }"
            PRIORITY="${ARGS%% *}"
            ARGS="${ARGS#$PRIORITY}"
            ;;
        --labels*)
            ARGS="${ARGS#--labels}"
            ARGS="${ARGS# }"
            if [[ "$ARGS" == \"* ]]; then
                EXTRA_LABELS="${ARGS#\"}"
                EXTRA_LABELS="${EXTRA_LABELS%%\"*}"
                ARGS="${ARGS#\"$EXTRA_LABELS\"}"
            else
                EXTRA_LABELS="${ARGS%% *}"
                ARGS="${ARGS#$EXTRA_LABELS}"
            fi
            ;;
        --spec*)
            ARGS="${ARGS#--spec}"
            ARGS="${ARGS# }"
            SPEC_NAME="${ARGS%% *}"
            ARGS="${ARGS#$SPEC_NAME}"
            if [ -d "specs/$SPEC_NAME" ]; then
                SPEC_LINK="specs/$SPEC_NAME"
            fi
            ;;
        --description*)
            ARGS="${ARGS#--description}"
            ARGS="${ARGS# }"
            if [[ "$ARGS" == \"* ]]; then
                DESCRIPTION="${ARGS#\"}"
                DESCRIPTION="${DESCRIPTION%%\"*}"
                ARGS="${ARGS#\"$DESCRIPTION\"}"
            else
                DESCRIPTION="${ARGS%% *}"
                ARGS="${ARGS#$DESCRIPTION}"
            fi
            ;;
        --create-spec*)
            ARGS="${ARGS#--create-spec}"
            CREATE_SPEC=true
            ;;
        \"*)
            # Quoted title
            ISSUE_TITLE="${ARGS#\"}"
            ISSUE_TITLE="${ISSUE_TITLE%%\"*}"
            ARGS="${ARGS#\"$ISSUE_TITLE\"}"
            ;;
        *)
            # Skip unknown or whitespace
            ARGS="${ARGS# }"
            [[ "$ARGS" == "$OLD_ARGS" ]] && break
            OLD_ARGS="$ARGS"
            ;;
    esac
    ARGS="${ARGS# }"
done

# Validate required fields
if [ -z "$ISSUE_TITLE" ]; then
    log_error "Issue title is required"
    echo ""
    echo "Usage: /speckle.issue \"<title>\" [--type <type>] [--priority <0-4>] [--labels <labels>]"
    echo ""
    echo "Examples:"
    echo "  /speckle.issue \"Add dark mode support\""
    echo "  /speckle.issue \"Login bug\" --type bug --priority 1"
    exit 1
fi

# Validate issue type
case "$ISSUE_TYPE" in
    feature|bug|enhancement|chore|docs) ;;
    *) 
        log_warn "Unknown type '$ISSUE_TYPE', defaulting to 'feature'"
        ISSUE_TYPE="feature"
        ;;
esac

# Set severity for bugs based on priority
SEVERITY=""
if [ "$ISSUE_TYPE" = "bug" ]; then
    case "$PRIORITY" in
        0) SEVERITY="critical" ;;
        1) SEVERITY="high" ;;
        2) SEVERITY="medium" ;;
        3|4) SEVERITY="low" ;;
    esac
fi

echo ""
echo "📝 Creating issue: $ISSUE_TITLE"
echo "   Type: $ISSUE_TYPE"
echo "   Priority: P$PRIORITY"
[ -n "$SEVERITY" ] && echo "   Severity: $SEVERITY"
[ -n "$EXTRA_LABELS" ] && echo "   Labels: $EXTRA_LABELS"
[ -n "$SPEC_LINK" ] && echo "   Spec: $SPEC_LINK"
echo ""
```

## Build Issue Body

```bash
# Select template based on type
TEMPLATE_PATH=".github/ISSUE_TEMPLATE/${ISSUE_TYPE}.md"
if [ -f "$TEMPLATE_PATH" ]; then
    # Use template as base
    BODY=$(cat "$TEMPLATE_PATH" | sed '/^---$/,/^---$/d')  # Remove front matter
else
    # Generate default body based on type
    case "$ISSUE_TYPE" in
        feature)
            BODY="## Summary

${DESCRIPTION:-Describe the feature...}

## Motivation

Why is this feature needed?

## Proposed Solution

How should this be implemented?

## Acceptance Criteria

- [ ] Criteria 1
- [ ] Criteria 2

## Additional Context

Add any other context or screenshots here."
            ;;
        bug)
            BODY="## Bug Description

${DESCRIPTION:-Describe the bug...}

## Steps to Reproduce

1. Step 1
2. Step 2
3. Step 3

## Expected Behavior

What should happen?

## Actual Behavior

What actually happens?

## Environment

- OS: 
- Version: 

## Severity

**${SEVERITY:-medium}**

## Additional Context

Add any other context or screenshots here."
            ;;
        enhancement)
            BODY="## Summary

${DESCRIPTION:-Describe the enhancement...}

## Current Behavior

How does it work now?

## Proposed Improvement

How should it work?

## Benefits

Why is this improvement valuable?

## Additional Context

Add any other context here."
            ;;
        chore)
            BODY="## Summary

${DESCRIPTION:-Describe the task...}

## Tasks

- [ ] Task 1
- [ ] Task 2

## Additional Context

Add any other context here."
            ;;
        docs)
            BODY="## Summary

${DESCRIPTION:-Describe the documentation needed...}

## Scope

What documentation needs to be created or updated?

## Sections

- [ ] Section 1
- [ ] Section 2

## Additional Context

Add any other context here."
            ;;
    esac
fi

# Add spec reference if linked
if [ -n "$SPEC_LINK" ]; then
    BODY="${BODY}

---

## Related Specification

📁 See [\`$SPEC_LINK\`]($SPEC_LINK/) for detailed specification."
fi

# Add Speckle footer
BODY="${BODY}

---
*Created via Speckle issue workflow*"
```

## Build Labels

```bash
# Start with type label
LABELS="$ISSUE_TYPE"

# Add severity for bugs
if [ "$ISSUE_TYPE" = "bug" ] && [ -n "$SEVERITY" ]; then
    LABELS="$LABELS,severity:$SEVERITY"
fi

# Add extra labels
if [ -n "$EXTRA_LABELS" ]; then
    LABELS="$LABELS,$EXTRA_LABELS"
fi

# Add spec label if linked
if [ -n "$SPEC_LINK" ]; then
    SPEC_NAME=$(basename "$SPEC_LINK")
    LABELS="$LABELS,spec:$SPEC_NAME"
fi

echo ""
echo "📋 Labels: $LABELS"
```

## Create GitHub Issue

```bash
echo ""
echo "Creating GitHub issue..."

# Create the issue
GH_ISSUE_URL=$(gh issue create \
    --title "$ISSUE_TITLE" \
    --body "$BODY" \
    --label "$LABELS" 2>&1)

if [ $? -ne 0 ]; then
    log_error "Failed to create GitHub issue"
    echo "$GH_ISSUE_URL"
    exit 1
fi

# Extract issue number
GH_ISSUE_NUM=$(echo "$GH_ISSUE_URL" | grep -oE '[0-9]+$')

echo ""
log_success "GitHub issue created: $GH_ISSUE_URL"
```

## Sync to Beads

```bash
echo ""
echo "Syncing to beads..."

# Map issue type to beads type
case "$ISSUE_TYPE" in
    feature)     BD_TYPE="feature" ;;
    bug)         BD_TYPE="bug" ;;
    enhancement) BD_TYPE="task" ;;
    chore)       BD_TYPE="task" ;;
    docs)        BD_TYPE="task" ;;
esac

# Create beads issue
BD_ISSUE_ID=$(bd create "$ISSUE_TITLE" \
    --type "$BD_TYPE" \
    --priority "${PRIORITY:-2}" \
    --labels "speckle,gh-$GH_ISSUE_NUM,$LABELS" \
    --description "## $ISSUE_TITLE

${DESCRIPTION:-See GitHub issue for details.}

### GitHub Reference
- Issue: #$GH_ISSUE_NUM
- URL: $GH_ISSUE_URL

---
*Synced from GitHub via Speckle*" 2>&1 | grep -oE 'speckle-[a-z0-9]+')

if [ -n "$BD_ISSUE_ID" ]; then
    log_success "Beads issue created: $BD_ISSUE_ID"
    
    # Add cross-reference comment to GitHub issue
    gh issue comment "$GH_ISSUE_NUM" --body "🔗 Tracked in beads: \`$BD_ISSUE_ID\`"
else
    log_warn "Could not create beads issue (non-fatal)"
fi
```

## Handle Spec Creation

```bash
if [ "$CREATE_SPEC" = true ]; then
    echo ""
    echo "📐 Spec creation suggested"
    echo ""
    echo "Next steps:"
    echo "  1. Create feature branch:"
    echo "     bd formula speckle-feature \"$ISSUE_TITLE\""
    echo ""
    echo "  2. Or manually create spec:"
    echo "     /speckit.specify \"$ISSUE_TITLE\""
fi
```

## Summary

```bash
echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ Issue created successfully!"
echo ""
echo "📋 Summary:"
echo "   Title: $ISSUE_TITLE"
echo "   Type: $ISSUE_TYPE"
echo "   GitHub: $GH_ISSUE_URL"
[ -n "$BD_ISSUE_ID" ] && echo "   Beads: $BD_ISSUE_ID"
[ -n "$SPEC_LINK" ] && echo "   Spec: $SPEC_LINK"
echo ""
echo "🎯 Next steps:"
if [ "$ISSUE_TYPE" = "bug" ]; then
    echo "   1. Reproduce the issue"
    echo "   2. Create a fix branch: /speckle.bugfix \"$ISSUE_TITLE\""
elif [ "$CREATE_SPEC" = true ]; then
    echo "   1. Create feature: bd formula speckle-feature \"$ISSUE_TITLE\""
    echo "   2. Develop spec: /speckit.specify"
    echo "   3. Plan: /speckit.plan"
    echo "   4. Tasks: /speckit.tasks"
    echo "   5. Sync: /speckle.sync"
else
    echo "   1. Start working on the issue"
    echo "   2. Update status: bd update $BD_ISSUE_ID --status in_progress"
    echo "   3. When done: bd close $BD_ISSUE_ID"
fi
echo "════════════════════════════════════════════════════════════"
```
