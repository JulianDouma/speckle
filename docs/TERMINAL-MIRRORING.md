# Terminal Mirroring for Speckle Board

Real-time terminal streaming for subagent processes, allowing you to monitor and interact with running agents directly from the kanban board.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Subagent      │────▶│   PTY Bridge     │────▶│  WebSocket      │
│   Process       │     │   (Python)       │     │  Server         │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │ WS
                                               ┌──────────▼────────┐
                                               │   Kanban Board    │
                                               │   (xterm.js)      │
                                               └───────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r .speckle/scripts/requirements-terminal.txt
```

### 2. Start Terminal Server

In a separate terminal:

```bash
python .speckle/scripts/terminal_server.py server
```

### 3. Start Kanban Board

```bash
python .speckle/scripts/board.py
```

### 4. Run Agent with Terminal Capture

```bash
# Using the launcher script
.speckle/scripts/terminal_launcher.sh speckle-abc claude --task "Implement feature"

# Or programmatically
python .speckle/scripts/terminal_server.py spawn speckle-abc -- bash
```

## Features

### Real-time Terminal Output
- Full ANSI color support
- Cursor movement and terminal sequences
- Scrollback history (5000 lines)

### Bidirectional Control
- Send keyboard input to running processes
- Send Ctrl+C (SIGINT) to interrupt
- Terminate process with SIGTERM/SIGKILL

### UI Components
- **Terminal Indicator**: Pulsing green dot on cards with active terminals
- **Inline Drawer**: Expand to see terminal in card
- **Full Screen Modal**: Press ⛶ for full-screen terminal view
- **Status Display**: Connection status indicator

## WebSocket Protocol

### Client → Server Messages

```json
// Subscribe to terminal output
{"type": "subscribe", "bead_id": "speckle-abc"}

// Unsubscribe
{"type": "unsubscribe", "bead_id": "speckle-abc"}

// Send keyboard input
{"type": "input", "bead_id": "speckle-abc", "data": "ls -la\n"}

// Send signal
{"type": "signal", "bead_id": "speckle-abc", "signal": "SIGINT"}

// Terminate process
{"type": "terminate", "bead_id": "speckle-abc"}

// Resize terminal
{"type": "resize", "bead_id": "speckle-abc", "rows": 24, "cols": 80}

// List all sessions
{"type": "list"}

// Spawn new terminal
{"type": "spawn", "bead_id": "speckle-xyz", "command": ["bash"], "cwd": "/path"}

// Get history
{"type": "history", "bead_id": "speckle-abc"}
```

### Server → Client Messages

```json
// Terminal output
{"type": "output", "bead_id": "speckle-abc", "data": "...", "timestamp": "..."}

// Initial buffer (scrollback)
{"type": "buffer", "bead_id": "speckle-abc", "data": "..."}

// Subscription confirmed
{"type": "subscribed", "bead_id": "speckle-abc"}

// Session terminated
{"type": "terminated", "bead_id": "speckle-abc"}

// Session list
{"type": "sessions", "sessions": [...]}

// Error
{"type": "error", "message": "..."}
```

## CLI Commands

```bash
# Start WebSocket server
python .speckle/scripts/terminal_server.py server --port 8421

# Spawn terminal for a bead
python .speckle/scripts/terminal_server.py spawn speckle-abc -- bash

# List active sessions
python .speckle/scripts/terminal_server.py list

# Terminate a session
python .speckle/scripts/terminal_server.py terminate speckle-abc

# View terminal history
python .speckle/scripts/terminal_server.py history speckle-abc --lines 100
```

## File Locations

| File | Purpose |
|------|---------|
| `.speckle/terminals/<bead-id>.json` | Session metadata (pid, command, etc.) |
| `.speckle/terminals/<bead-id>.log` | Terminal output log (persisted) |
| `.speckle/scripts/terminal_server.py` | WebSocket server and PTY bridge |
| `.speckle/scripts/terminal_launcher.sh` | Shell wrapper for terminal capture |

## Integration with speckle.loop

To enable terminal mirroring for speckle.loop tasks:

1. Ensure terminal server is running
2. The loop will automatically create terminal sessions for in-progress beads
3. View terminals in the kanban board's IN PROGRESS column

## Security Considerations

- Terminal server binds to `localhost` by default
- User input is forwarded directly to the PTY (be cautious)
- Consider running in isolated environments for sensitive operations

## Troubleshooting

### "No active terminal session"
- Ensure the terminal server is running
- Check that the bead ID matches an active session
- Look for session files in `.speckle/terminals/`

### WebSocket connection failed
- Check if terminal server is running on the correct port
- Verify no firewall is blocking localhost connections

### Terminal output not updating
- Check browser console for WebSocket errors
- Verify the session is still active (`python terminal_server.py list`)
