---
description: Run Ralph-style iterative execution loop until all tasks complete
---

# Speckle Loop

Runs an autonomous implementation loop following the Ralph pattern: fresh context per task, 
progress persistence, and DoD verification. Continues until all tasks pass or max iterations reached.

## Arguments

```text
$ARGUMENTS
```

Options:
- No args: Run until all tasks complete (max 10 iterations)
- `--max N`: Set maximum iterations (default: 10)
- `--verify`: Run DoD verifiers before closing tasks
- `--dry-run`: Show execution plan without running
- `--continue`: Resume from previous progress

## The Ralph Pattern

Each iteration:
1. Pick highest-priority ready task
2. Spawn fresh context (clean slate)
3. Implement single task
4. Run quality checks
5. Commit changes
6. Record learnings to progress.txt
7. Close task
8. Repeat

Memory persists via:
- Git history (commits)
- `.speckle/progress.txt` (learnings)
- Bead status (which tasks done)

## Startup Checks

```bash
# Source helpers
source ".speckle/scripts/common.sh"
source ".speckle/scripts/loop.sh"

# Parse arguments
MAX_ITERATIONS=10
VERIFY_DOD=false
DRY_RUN=false
CONTINUE_MODE=false

for arg in $ARGUMENTS; do
    case "$arg" in
        --max) shift; MAX_ITERATIONS="${1:-10}" ;;
        --verify) VERIFY_DOD=true ;;
        --dry-run) DRY_RUN=true ;;
        --continue) CONTINUE_MODE=true ;;
    esac
done

# Verify beads is available
if ! bd ready &>/dev/null; then
    log_error "Beads not available or no issues synced"
    echo "   Run /speckle.sync first"
    exit 1
fi

# Ensure progress file exists
PROGRESS_FILE=".speckle/progress.txt"
mkdir -p "$(dirname "$PROGRESS_FILE")"
touch "$PROGRESS_FILE"

log_success "Speckle Loop initialized"
echo "📊 Max iterations: $MAX_ITERATIONS"
echo "🔍 DoD verification: $VERIFY_DOD"
echo "📝 Progress file: $PROGRESS_FILE"
```

## Load Previous Progress

```bash
if [ "$CONTINUE_MODE" = true ] && [ -s "$PROGRESS_FILE" ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "📜 Previous Session Learnings"
    echo "═══════════════════════════════════════════════════════════"
    # Show last 20 lines of progress
    tail -50 "$PROGRESS_FILE" | head -20
    echo "═══════════════════════════════════════════════════════════"
    echo ""
fi
```

## Execution Plan (Dry Run)

```bash
if [ "$DRY_RUN" = true ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "🔮 Execution Plan (Dry Run)"
    echo "═══════════════════════════════════════════════════════════"
    
    # Get all ready tasks
    READY_TASKS=$(bd ready 2>/dev/null || echo "")
    TASK_COUNT=$(echo "$READY_TASKS" | grep -c "^" || echo "0")
    
    echo "Ready tasks: $TASK_COUNT"
    echo ""
    echo "$READY_TASKS"
    echo ""
    echo "Would run up to $MAX_ITERATIONS iterations"
    echo "═══════════════════════════════════════════════════════════"
    exit 0
fi
```

## Main Loop

The loop spawns fresh agent contexts for each task using the Task tool.

```markdown
## Loop Execution

I will now run the implementation loop. For each iteration:

1. **Check for ready tasks** using `bd ready`
2. **Select highest priority task** 
3. **Spawn fresh implementation context** using Task tool
4. **Wait for completion**
5. **Verify and close task**
6. **Record progress**
7. **Continue or exit**

### Iteration Control

- Current iteration: 1
- Max iterations: {MAX_ITERATIONS}
- Tasks remaining: (check with `bd ready`)

### Per-Task Workflow

For each task, I will use the Task tool to spawn a fresh agent that:

1. Claims the task (`bd update <id> --status in_progress`)
2. Reads task details (`bd show <id>`)
3. Implements the solution
4. Commits changes
5. Reports back completion status

Then I will:
1. Run DoD verifiers (if --verify)
2. Record learnings to progress.txt
3. Close the task (`bd close <id>`)
4. Check for next task

### Stop Conditions

The loop exits when:
- No ready tasks remain (SUCCESS - all work complete)
- Max iterations reached (PAUSE - manual review needed)
- Critical error occurs (FAIL - needs intervention)
```

## Task Implementation Prompt

When spawning fresh context for each task, use this prompt template:

```markdown
## Fresh Implementation Context

You are implementing a single task with fresh context. 

### Your Task
{TASK_TITLE}

### Description
{TASK_DESCRIPTION}

### Constraints
- Complete THIS TASK ONLY
- Make atomic, focused changes
- Test your changes
- Commit with clear message: `type(scope): description`

### Previous Learnings
Check .speckle/progress.txt for context from previous iterations.

### Definition of Done
1. Code compiles/runs without errors
2. Tests pass (if applicable)
3. Changes committed to git
4. No untracked files left behind

### When Complete
Report back:
- What you implemented
- Files changed
- Any issues encountered
- Learnings for future tasks
```

## DoD Verification

```bash
run_dod_verifiers() {
    local bead_id="$1"
    
    if [ "$VERIFY_DOD" != true ]; then
        return 0
    fi
    
    log_info "Running DoD verifiers..."
    
    # Standard verifiers
    local failed=0
    
    # 1. Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        log_warn "Uncommitted changes detected"
        failed=1
    fi
    
    # 2. Run tests if test command exists
    if [ -f "Makefile" ] && grep -q "^test:" Makefile; then
        log_info "Running: make test"
        if ! make test; then
            log_error "Tests failed"
            failed=1
        fi
    elif [ -f "package.json" ] && grep -q '"test"' package.json; then
        log_info "Running: npm test"
        if ! npm test; then
            log_error "Tests failed"
            failed=1
        fi
    fi
    
    # 3. Run lint if available
    if [ -f "Makefile" ] && grep -q "^lint:" Makefile; then
        log_info "Running: make lint"
        if ! make lint; then
            log_warn "Lint warnings (non-blocking)"
        fi
    fi
    
    return $failed
}
```

## Record Progress

```bash
record_progress() {
    local bead_id="$1"
    local task_title="$2"
    local iteration="$3"
    local status="$4"
    local learnings="$5"
    
    local timestamp
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    cat >> "$PROGRESS_FILE" <<EOF

---
## Iteration $iteration: $task_title
**Bead:** $bead_id
**Time:** $timestamp
**Status:** $status

### Learnings
$learnings

### Git State
$(git log -1 --oneline 2>/dev/null || echo "No commits")

EOF
    
    log_success "Progress recorded to $PROGRESS_FILE"
}
```

## Loop Runner

Execute the main loop:

```markdown
## Starting Loop Execution

I will now iterate through ready tasks. Each task gets fresh context.

### Iteration Process

For iteration N (1 to MAX_ITERATIONS):

1. **Get next task:**
   ```bash
   bd ready --json | jq -r '.[0]'
   ```

2. **If no tasks:** Output `<loop>COMPLETE</loop>` and exit

3. **Spawn fresh implementation:** Use Task tool with:
   - subagent_type: "general"
   - Detailed task prompt with context
   - Instructions to implement and report back

4. **On completion:**
   - Run DoD verifiers
   - Record progress
   - Close task: `bd close <bead_id>`

5. **Continue to next iteration**

### Output Markers

- `<loop>COMPLETE</loop>` - All tasks done
- `<loop>PAUSED</loop>` - Max iterations reached
- `<loop>FAILED</loop>` - Critical error

Let me begin the loop now...
```

## Completion Summary

After loop exits, show summary:

```bash
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📊 Loop Execution Summary"
echo "═══════════════════════════════════════════════════════════"

# Count completed in this session
COMPLETED=$(grep -c "^## Iteration" "$PROGRESS_FILE" 2>/dev/null || echo "0")
echo "Tasks completed this session: $COMPLETED"

# Show remaining
REMAINING=$(bd ready 2>/dev/null | grep -c "^" || echo "0")
echo "Tasks remaining: $REMAINING"

# Show recent progress
echo ""
echo "Recent learnings:"
tail -20 "$PROGRESS_FILE" | grep -A2 "### Learnings" | head -10

echo ""
echo "═══════════════════════════════════════════════════════════"

if [ "$REMAINING" -eq 0 ]; then
    echo "🎉 ALL TASKS COMPLETE!"
    echo "<loop>COMPLETE</loop>"
else
    echo "⏸️  Loop paused - $REMAINING tasks remain"
    echo "   Run /speckle.loop --continue to resume"
    echo "<loop>PAUSED</loop>"
fi
```
