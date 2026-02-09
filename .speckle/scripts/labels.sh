#!/usr/bin/env bash
# Speckle label generation helper functions
# Source this in commands: source ".speckle/scripts/labels.sh"

set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Slugify a string for use as a label value
# - Converts to lowercase
# - Replaces spaces and special chars with hyphens
# - Removes consecutive hyphens
# - Removes leading/trailing hyphens
#
# Arguments:
#   $1 - String to slugify
# Returns: Slugified string
slugify() {
    local input="${1:-}"
    echo "$input" | \
        tr '[:upper:]' '[:lower:]' | \
        sed 's/[^a-z0-9]/-/g' | \
        sed 's/--*/-/g' | \
        sed 's/^-//' | \
        sed 's/-$//'
}

# Extract phase label from a phase/section name
# Arguments:
#   $1 - Phase name (e.g., "Phase 1: Foundation", "User Story 2 - Filtering")
# Returns: Label string like "phase:foundation" or "phase:us2-filtering"
extract_phase_label() {
    local phase_name="${1:-}"
    
    if [ -z "$phase_name" ]; then
        echo "phase:unassigned"
        return
    fi
    
    # Remove common prefixes like "Phase X:" or "Phase X -"
    local cleaned
    cleaned=$(echo "$phase_name" | sed -E 's/^Phase [0-9]+[:\-]?\s*//i')
    
    # Handle "User Story X" format
    cleaned=$(echo "$cleaned" | sed -E 's/^User Story ([0-9]+)\s*[-:]\s*/us\1-/i')
    
    # Slugify the result
    local slug
    slug=$(slugify "$cleaned")
    
    # Ensure we have something
    if [ -z "$slug" ]; then
        echo "phase:unassigned"
    else
        echo "phase:$slug"
    fi
}

# Extract story label from task markers like [US1], [US2], etc.
# Arguments:
#   $1 - Task line or description containing [USx] marker
# Returns: Label string like "story:us1" or empty if no marker
extract_story_label() {
    local task_text="${1:-}"
    
    # Look for [US#] or [USx] pattern
    local story_match
    story_match=$(echo "$task_text" | grep -oE '\[US[0-9]+\]' | head -1 || echo "")
    
    if [ -n "$story_match" ]; then
        # Extract just the number and format
        local story_num
        story_num=$(echo "$story_match" | grep -oE '[0-9]+')
        echo "story:us$story_num"
    fi
}

# Check if task has parallel marker [P]
# Arguments:
#   $1 - Task line or description
# Returns: "parallel" if has marker, empty otherwise
extract_parallel_label() {
    local task_text="${1:-}"
    
    if echo "$task_text" | grep -qE '\[P\]'; then
        echo "parallel"
    fi
}

# Extract feature label from git branch name
# Arguments:
#   $1 - Branch name (optional, defaults to current branch)
# Returns: Label string like "feature:001-comments-integration"
extract_feature_label() {
    local branch="${1:-}"
    
    if [ -z "$branch" ]; then
        branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
    fi
    
    # Skip if on main/master
    if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then
        return
    fi
    
    local slug
    slug=$(slugify "$branch")
    
    if [ -n "$slug" ]; then
        echo "feature:$slug"
    fi
}

# Build a complete label string for a task
# Combines all applicable labels into comma-separated string
#
# Arguments:
#   $1 - Task text/description
#   $2 - Phase name (from current markdown section)
#   $3 - Branch name (optional)
#   $4 - Additional labels (optional, comma-separated)
# Returns: Comma-separated label string
build_label_string() {
    local task_text="${1:-}"
    local phase_name="${2:-}"
    local branch="${3:-}"
    local extra_labels="${4:-}"
    
    local labels=()
    
    # Always add speckle label
    labels+=("speckle")
    
    # Add feature label
    local feature_label
    feature_label=$(extract_feature_label "$branch")
    if [ -n "$feature_label" ]; then
        labels+=("$feature_label")
    fi
    
    # Add phase label
    local phase_label
    phase_label=$(extract_phase_label "$phase_name")
    if [ -n "$phase_label" ]; then
        labels+=("$phase_label")
    fi
    
    # Add story label
    local story_label
    story_label=$(extract_story_label "$task_text")
    if [ -n "$story_label" ]; then
        labels+=("$story_label")
    fi
    
    # Add parallel label
    local parallel_label
    parallel_label=$(extract_parallel_label "$task_text")
    if [ -n "$parallel_label" ]; then
        labels+=("$parallel_label")
    fi
    
    # Add any extra labels
    if [ -n "$extra_labels" ]; then
        IFS=',' read -ra EXTRA <<< "$extra_labels"
        for label in "${EXTRA[@]}"; do
            label=$(echo "$label" | xargs)  # trim whitespace
            if [ -n "$label" ]; then
                labels+=("$label")
            fi
        done
    fi
    
    # Join with commas (max 10 labels to avoid issues)
    local count=0
    local result=""
    for label in "${labels[@]}"; do
        if [ $count -ge 10 ]; then
            break
        fi
        if [ -n "$result" ]; then
            result="$result,$label"
        else
            result="$label"
        fi
        ((count++))
    done
    
    echo "$result"
}

# Get all unique phase labels from issues
# Returns: Newline-separated list of phase labels
get_phase_labels() {
    bd list 2>/dev/null | \
        grep -oE 'phase:[a-z0-9-]+' | \
        sort -u || echo ""
}

# Count issues by label
# Arguments:
#   $1 - Label to count (e.g., "phase:foundation")
#   $2 - Status filter (optional, e.g., "closed")
# Returns: Count
count_by_label() {
    local label="${1:-}"
    local status="${2:-}"
    
    local cmd="bd list"
    if [ -n "$status" ]; then
        cmd="$cmd --status $status"
    fi
    
    $cmd 2>/dev/null | grep -c "$label" || echo "0"
}

# Export functions
export -f slugify
export -f extract_phase_label
export -f extract_story_label
export -f extract_parallel_label
export -f extract_feature_label
export -f build_label_string
export -f get_phase_labels
export -f count_by_label
