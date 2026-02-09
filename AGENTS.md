# Agent Instructions

## ⚠️ CRITICAL: Self-Hosted Development

**This is the Speckle project itself. All work MUST be tracked as Speckle beads.**

We develop **Speckle using Speckle** - dogfooding is mandatory.

### Essential Commands

```bash
# Find work
bd ready                          # Shows prioritized ready tasks

# Do work  
bd update <id> --status in_progress   # Claim task
# ... implement ...
bd close <id>                     # Complete task

# Create issues
bd create "Title" --type bug      # Bug report
bd create "Title" --type task     # Task
bd create "Title" --type feature  # Feature request

# Sync
bd sync                           # Sync with git (before push)
```

### Rules

| Rule | Description |
|------|-------------|
| **All issues use `speckle-` prefix** | Configured in `.beads/config.toml` |
| **Track via beads** | Use `bd ready`, `bd close` - not external trackers |
| **Comments preserve memory** | Use `bd comments <id> add "note"` for context |

### Spec-Kit Integration (Optional)

For larger features with formal planning:

```bash
# 1. Create spec, plan, tasks (spec-kit)
specify spec "Feature Name"
specify plan
specify tasks

# 2. Sync to beads (Speckle bridge)
# Manually: review tasks.md, create beads issues
# Or if /speckle.sync works: /speckle.sync

# 3. Execute via beads
bd ready && bd close <id>
```

See [docs/SELF-HOSTING.md](docs/SELF-HOSTING.md) for dogfooding philosophy.

---

## Quick Reference

```bash
bd ready              # Find available work (prioritized)
bd show <id>          # View issue details  
bd close <id>         # Complete work
bd sync               # Sync with git
```

## Session Completion

Work is complete only after `git push` succeeds.

### Checklist

1. **Close completed issues**: `bd close <id>`
2. **File issues for remaining work**: `bd create "Title"`
3. **Sync and push**:
   ```bash
   bd sync && git pull --rebase && git push
   ```
4. **Hand off**: summarize progress and next steps

If push fails, resolve conflicts and retry until successful.
