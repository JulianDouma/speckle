#!/usr/bin/env bash
#
# Terminal Mirroring Demo
# 
# This script demonstrates the terminal mirroring feature by:
# 1. Starting the terminal server
# 2. Creating a demo bead
# 3. Starting the kanban board
# 4. Running a demo task with terminal capture
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[demo]${NC} $*"
}

success() {
    echo -e "${GREEN}✓${NC} $*"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $*"
}

error() {
    echo -e "${RED}✗${NC} $*"
}

# Check dependencies
check_deps() {
    log "Checking dependencies..."
    
    if ! python3 -c "import websockets" 2>/dev/null; then
        warn "websockets not installed. Installing..."
        pip3 install websockets
    fi
    
    if ! command -v bd &>/dev/null; then
        error "bd command not found. Make sure beads is installed."
        exit 1
    fi
    
    success "Dependencies OK"
}

# Start terminal server in background
start_terminal_server() {
    log "Starting terminal server..."
    
    # Kill any existing terminal server
    pkill -f "terminal_server.py server" 2>/dev/null || true
    sleep 1
    
    python3 "$SCRIPT_DIR/terminal_server.py" server &
    TERMINAL_PID=$!
    
    sleep 2
    
    if kill -0 $TERMINAL_PID 2>/dev/null; then
        success "Terminal server running (PID: $TERMINAL_PID)"
    else
        error "Failed to start terminal server"
        exit 1
    fi
}

# Create demo bead
create_demo_bead() {
    log "Creating demo bead..."
    
    DEMO_ID=$(bd create --title "Terminal Demo Task" --type task --priority 2 2>&1 | grep -oE 'speckle-[a-z0-9]+')
    
    if [[ -n "$DEMO_ID" ]]; then
        bd update "$DEMO_ID" --status in_progress
        success "Created bead: $DEMO_ID"
    else
        error "Failed to create demo bead"
        exit 1
    fi
}

# Run demo task with terminal capture
run_demo_task() {
    log "Starting demo task with terminal capture..."
    
    # Create terminal directory
    mkdir -p .speckle/terminals
    
    # Create session info
    cat > ".speckle/terminals/$DEMO_ID.json" <<EOF
{
  "bead_id": "$DEMO_ID",
  "pid": $$,
  "command": "demo-task",
  "cwd": "$(pwd)",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "last_activity": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "active": true
}
EOF
    
    # Spawn demo task (simple countdown)
    python3 "$SCRIPT_DIR/terminal_server.py" spawn "$DEMO_ID" -- bash -c '
        echo "🎬 Terminal Mirroring Demo"
        echo "=========================="
        echo ""
        echo "This terminal output is being streamed to the kanban board!"
        echo ""
        for i in 10 9 8 7 6 5 4 3 2 1; do
            echo "Countdown: $i..."
            sleep 1
        done
        echo ""
        echo "✅ Demo complete!"
        echo ""
        echo "Try these in the board:"
        echo "  • Click the Terminal button on the card"
        echo "  • Type in the terminal to send input"
        echo "  • Click Ctrl+C to send interrupt"
        echo "  • Click Terminate to stop the process"
        echo ""
        echo "Waiting for input (type something and press Enter)..."
        read -r input
        echo "You typed: $input"
        echo ""
        echo "Demo session ending in 5 seconds..."
        sleep 5
    ' &
    TASK_PID=$!
    
    success "Demo task running (PID: $TASK_PID)"
}

# Start board
start_board() {
    log "Starting kanban board..."
    
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  Terminal Mirroring Demo"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "  📋 Demo bead: $DEMO_ID"
    echo ""
    echo "  The board will open in your browser."
    echo "  Look for the card in the IN PROGRESS column."
    echo "  Click 'Terminal' to view the live terminal output."
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo ""
    
    python3 "$SCRIPT_DIR/board.py" --refresh 3
}

# Cleanup
cleanup() {
    log "Cleaning up..."
    
    # Kill terminal server
    if [[ -n "${TERMINAL_PID:-}" ]]; then
        kill $TERMINAL_PID 2>/dev/null || true
    fi
    
    # Kill demo task
    if [[ -n "${TASK_PID:-}" ]]; then
        kill $TASK_PID 2>/dev/null || true
    fi
    
    # Close demo bead
    if [[ -n "${DEMO_ID:-}" ]]; then
        bd close "$DEMO_ID" --reason "Demo completed" 2>/dev/null || true
    fi
    
    # Remove session files
    rm -f ".speckle/terminals/$DEMO_ID.json" 2>/dev/null || true
    rm -f ".speckle/terminals/$DEMO_ID.log" 2>/dev/null || true
    
    success "Cleanup complete"
}

trap cleanup EXIT

# Main
main() {
    echo ""
    echo "🔮 Speckle Terminal Mirroring Demo"
    echo ""
    
    check_deps
    start_terminal_server
    create_demo_bead
    run_demo_task
    start_board
}

main "$@"
