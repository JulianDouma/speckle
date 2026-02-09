---
description: Synchronize spec-kit tasks.md with beads issue tracking (bidirectional)
---

# Speckle Sync

Bidirectional synchronization between `tasks.md` (planning) and beads (execution tracking).

## Arguments

```text
$ARGUMENTS
```

Options:
- `--dry-run` - Show what would be done without making changes
- `--force` - Force re-sync even if recently synced

## Prerequisites

```bash
# Source helpers
source ".speckle/scripts/common.sh"
source ".speckle/scripts/labels.sh"
source ".speckle/scripts/epics.sh"

# Parse arguments
DRY_RUN=""
FORCE=""
if [[ "$ARGUMENTS" == *"--dry-run"* ]]; then
    DRY_RUN="true"
    log_info "Dry run mode - no changes will be made"
fi
if [[ "$ARGUMENTS" == *"--force"* ]]; then
    FORCE="true"
fi

# Check beads is available
if ! command -v bd &> /dev/null; then
    log_error "Beads not installed. Install from: https://github.com/steveyegge/beads"
    exit 1
fi

# Check jq is available
if ! command -v jq &> /dev/null; then
    log_error "jq not installed. Install from: https://stedolan.github.io/jq/"
    exit 1
fi

# Find feature directory (spec-kit convention: specs/NNN-feature-name/)
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
if [[ ! "$BRANCH" =~ ^[0-9]{3}- ]]; then
    log_error "Not on a feature branch. Expected: NNN-feature-name"
    echo "   Current branch: $BRANCH"
    exit 1
fi

PREFIX="${BRANCH:0:3}"
FEATURE_DIR=$(find specs -maxdepth 1 -type d -name "${PREFIX}-*" 2>/dev/null | head -1)

if [ -z "$FEATURE_DIR" ] || [ ! -f "$FEATURE_DIR/tasks.md" ]; then
    log_error "tasks.md not found. Run /speckit.tasks first."
    exit 1
fi

echo "📁 Feature: $FEATURE_DIR"
```

## Load Context

```bash
SPEC_FILE="$FEATURE_DIR/spec.md"
PLAN_FILE="$FEATURE_DIR/plan.md"
TASKS_FILE="$FEATURE_DIR/tasks.md"
MAPPING_FILE="$FEATURE_DIR/.speckle-mapping.json"

# Initialize mapping if not exists
if [ ! -f "$MAPPING_FILE" ]; then
    cat > "$MAPPING_FILE" << EOF
{
  "version": 1,
  "feature": "$BRANCH",
  "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "tasks": {}
}
EOF
    log_info "Created new mapping file"
fi
```

## Create/Load Epic

```bash
# Check if epic already exists for this feature
EPIC_ID=$(get_epic_id "$MAPPING_FILE")

if [ -z "$EPIC_ID" ]; then
    if [ -n "$DRY_RUN" ]; then
        log_info "[DRY RUN] Would create epic for $BRANCH"
        EPIC_ID="dry-run-epic"
    else
        # Create new epic from spec
        EPIC_ID=$(create_epic "$BRANCH" "$SPEC_FILE")
        
        # Save epic ID to mapping
        save_epic_id "$MAPPING_FILE" "$EPIC_ID"
        
        log_success "Created epic: $EPIC_ID"
    fi
else
    echo "🎯 Using existing epic: $EPIC_ID"
fi
```

## Parse Tasks

Extract tasks from tasks.md using bash regex:

```bash
# Task line format: - [ ] T001 [P] [US1] Description
# - [ ] = incomplete, - [x] = complete
# T001 = task ID
# [P] = parallel (optional)
# [US1] = user story (optional)

CURRENT_PHASE="default"
TASKS_CREATED=0
TASKS_SYNCED=0
TASKS_TOTAL=0

echo ""
echo "📋 Parsing tasks.md..."
echo ""

while IFS= read -r line || [ -n "$line" ]; do
    # Track phase headers (## or ### followed by text)
    if [[ "$line" =~ ^##[#]?[[:space:]]+(.+)$ ]]; then
        CURRENT_PHASE="${BASH_REMATCH[1]}"
        continue
    fi
    
    # Match task lines: - [ ] T001 [P] [US1] Description
    # or: - [x] T001 [P] [US1] Description
    if [[ "$line" =~ ^-[[:space:]]+\[([[:space:]x])\][[:space:]]+(T[0-9]{3})[[:space:]]*(\[P\])?[[:space:]]*(\[US[0-9]+\])?[[:space:]]*(.+)$ ]]; then
        TASK_COMPLETED="${BASH_REMATCH[1]}"
        TASK_ID="${BASH_REMATCH[2]}"
        TASK_PARALLEL="${BASH_REMATCH[3]}"
        TASK_STORY="${BASH_REMATCH[4]}"
        TASK_DESC="${BASH_REMATCH[5]}"
        
        # Clean up story (remove brackets)
        TASK_STORY="${TASK_STORY//[\[\]]/}"
        
        ((TASKS_TOTAL++)) || true
        
        # Check if task is completed
        IS_COMPLETED=""
        if [ "$TASK_COMPLETED" = "x" ]; then
            IS_COMPLETED="true"
        fi
        
        # Check if task already has a bead
        EXISTING_BEAD=$(jq -r ".tasks[\"$TASK_ID\"].beadId // empty" "$MAPPING_FILE" 2>/dev/null)
        
        if [ -n "$EXISTING_BEAD" ]; then
            # Task exists - reconcile status
            BEAD_STATUS=$(bd show "$EXISTING_BEAD" 2>/dev/null | grep -oE 'OPEN|IN_PROGRESS|CLOSED|BLOCKED' | head -1 || echo "unknown")
            BEAD_STATUS=$(echo "$BEAD_STATUS" | tr '[:upper:]' '[:lower:]')
            
            if [ "$BEAD_STATUS" = "closed" ] && [ -z "$IS_COMPLETED" ]; then
                # Bead closed but task not checked - mark in tasks.md
                if [ -n "$DRY_RUN" ]; then
                    log_info "[DRY RUN] Would mark $TASK_ID complete (bead is closed)"
                else
                    # Update tasks.md to mark task complete
                    sed -i.bak "s/- \[ \] $TASK_ID/- [x] $TASK_ID/" "$TASKS_FILE"
                    rm -f "${TASKS_FILE}.bak"
                    log_success "Marked $TASK_ID complete (synced from beads)"
                fi
                ((TASKS_SYNCED++)) || true
            elif [ -n "$IS_COMPLETED" ] && [ "$BEAD_STATUS" != "closed" ]; then
                # Task checked but bead open - close bead
                if [ -n "$DRY_RUN" ]; then
                    log_info "[DRY RUN] Would close $EXISTING_BEAD (task is checked)"
                else
                    bd close "$EXISTING_BEAD" -r "Synced from tasks.md" 2>/dev/null || true
                    log_success "Closed $EXISTING_BEAD (synced from tasks.md)"
                fi
                ((TASKS_SYNCED++)) || true
            else
                echo "   ✓ $TASK_ID → $EXISTING_BEAD (in sync)"
            fi
        elif [ -z "$IS_COMPLETED" ]; then
            # New task - create bead issue
            if [ -n "$DRY_RUN" ]; then
                log_info "[DRY RUN] Would create bead for $TASK_ID: $TASK_DESC"
                ((TASKS_CREATED++)) || true
            else
                # Determine priority from phase
                PRIORITY=2
                if [[ "$CURRENT_PHASE" =~ [Ff]oundation|[Ss]etup|[Pp]hase[[:space:]]*1 ]]; then
                    PRIORITY=1
                elif [ "$TASK_STORY" = "US1" ]; then
                    PRIORITY=2
                else
                    PRIORITY=3
                fi
                
                # Build labels
                LABELS="speckle,task:$TASK_ID"
                [ -n "$TASK_STORY" ] && LABELS="$LABELS,story:$(echo "$TASK_STORY" | tr '[:upper:]' '[:lower:]')"
                [ -n "$TASK_PARALLEL" ] && LABELS="$LABELS,parallel"
                LABELS="$LABELS,phase:$(slugify "$CURRENT_PHASE")"
                LABELS="$LABELS,feature:$BRANCH"
                
                # Create description
                DESCRIPTION="## Task: $TASK_DESC

### Metadata
- **Task ID**: $TASK_ID
- **Phase**: $CURRENT_PHASE
- **Story**: ${TASK_STORY:-N/A}
- **Parallel**: ${TASK_PARALLEL:+Yes}${TASK_PARALLEL:-No}
- **Source**: $TASKS_FILE

---
*Synced by Speckle*"

                # Truncate description for title
                TITLE_DESC="${TASK_DESC:0:60}"
                [ "${#TASK_DESC}" -gt 60 ] && TITLE_DESC="${TITLE_DESC}..."
                
                # Create bead issue
                NEW_BEAD=$(bd create "$TASK_ID: $TITLE_DESC" \
                    --type task \
                    --priority "$PRIORITY" \
                    --labels "$LABELS" \
                    --description "$DESCRIPTION" \
                    2>&1 | grep -oE 'speckle-[a-z0-9]+' || echo "")
                
                if [ -n "$NEW_BEAD" ]; then
                    # Update mapping with new bead
                    TEMP_FILE="${MAPPING_FILE}.tmp.$$"
                    jq --arg id "$TASK_ID" --arg bead "$NEW_BEAD" \
                        '.tasks[$id] = {"beadId": $bead, "created": (now | strftime("%Y-%m-%dT%H:%M:%SZ"))}' \
                        "$MAPPING_FILE" > "$TEMP_FILE" && mv "$TEMP_FILE" "$MAPPING_FILE"
                    
                    # Link to epic
                    if [ -n "$EPIC_ID" ] && [ "$EPIC_ID" != "dry-run-epic" ]; then
                        link_task_to_epic "$NEW_BEAD" "$EPIC_ID" 2>/dev/null || true
                    fi
                    
                    log_success "Created $NEW_BEAD for $TASK_ID"
                    ((TASKS_CREATED++)) || true
                else
                    log_error "Failed to create bead for $TASK_ID"
                fi
            fi
        fi
    fi
done < "$TASKS_FILE"
```

## Update Mapping Timestamp

```bash
if [ -z "$DRY_RUN" ]; then
    TEMP_FILE="${MAPPING_FILE}.tmp.$$"
    jq --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '.lastSync = $ts' "$MAPPING_FILE" > "$TEMP_FILE" && mv "$TEMP_FILE" "$MAPPING_FILE"
fi
```

## Update Epic Status

```bash
if [ -n "$EPIC_ID" ] && [ "$EPIC_ID" != "dry-run-epic" ] && [ -z "$DRY_RUN" ]; then
    NEW_STATUS=$(update_epic_status "$EPIC_ID" "$MAPPING_FILE")
    if [ -n "$NEW_STATUS" ]; then
        echo ""
        echo "📊 Epic status: $NEW_STATUS"
    fi
fi
```

## Summary

```bash
echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ Speckle Sync Complete"
echo ""
echo "📊 Summary:"
echo "   Tasks in tasks.md: $TASKS_TOTAL"
echo "   New beads created: $TASKS_CREATED"
echo "   Status synced: $TASKS_SYNCED"
echo ""
echo "📁 Mapping: $MAPPING_FILE"
echo ""
if [ -n "$DRY_RUN" ]; then
    echo "ℹ️  This was a dry run - no changes were made"
    echo "   Run without --dry-run to apply changes"
else
    echo "🎯 Next: Run \`bd ready\` to see available work"
fi
echo "════════════════════════════════════════════════════════════"
```
