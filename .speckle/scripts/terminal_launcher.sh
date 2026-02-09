#!/usr/bin/env bash
#
# Speckle Terminal Launcher
# Wraps subagent commands with terminal capture for real-time mirroring.
#
# Usage:
#   terminal_launcher.sh <bead-id> <command> [args...]
#
# Example:
#   terminal_launcher.sh speckle-abc claude --task "Implement feature"
#
# The script:
# 1. Creates a terminal session for the bead
# 2. Runs the command with PTY capture
# 3. Logs output to .speckle/terminals/<bead-id>.log
# 4. Creates session info in .speckle/terminals/<bead-id>.json
#

set -euo pipefail

# === Configuration ===
TERMINAL_DIR=".speckle/terminals"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# === Helpers ===
log() {
    echo "[terminal-launcher] $*" >&2
}

# === Main ===
main() {
    if [[ $# -lt 2 ]]; then
        echo "Usage: $0 <bead-id> <command> [args...]"
        echo ""
        echo "Examples:"
        echo "  $0 speckle-abc bash"
        echo "  $0 speckle-abc claude --task 'Implement feature'"
        exit 1
    fi

    local bead_id="$1"
    shift
    local cmd=("$@")

    # Create terminal directory
    mkdir -p "$TERMINAL_DIR"

    # Clean up old session files
    rm -f "$TERMINAL_DIR/$bead_id.json" 2>/dev/null || true

    # Create session info
    local session_file="$TERMINAL_DIR/$bead_id.json"
    local log_file="$TERMINAL_DIR/$bead_id.log"
    local start_time
    start_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    cat > "$session_file" <<EOF
{
  "bead_id": "$bead_id",
  "pid": $$,
  "command": "${cmd[*]}",
  "cwd": "$(pwd)",
  "created_at": "$start_time",
  "last_activity": "$start_time",
  "active": true
}
EOF

    log "Starting terminal session for $bead_id"
    log "Command: ${cmd[*]}"
    log "Log: $log_file"

    # Set up cleanup handler
    cleanup() {
        log "Cleaning up session $bead_id"
        rm -f "$session_file" 2>/dev/null || true
    }
    trap cleanup EXIT

    # Set terminal environment
    export TERM="${TERM:-xterm-256color}"
    export COLORTERM="truecolor"
    export SPECKLE_BEAD_ID="$bead_id"
    export SPECKLE_TERMINAL="1"

    # Clear previous log (keep only current session)
    : > "$log_file"

    # Run command with script to capture output
    # Using script command for PTY emulation on macOS/Linux
    if [[ "$(uname)" == "Darwin" ]]; then
        # macOS version
        script -q "$log_file" "${cmd[@]}"
    else
        # Linux version
        script -q -c "${cmd[*]}" "$log_file"
    fi

    local exit_code=$?

    log "Session ended with exit code $exit_code"
    return $exit_code
}

main "$@"
