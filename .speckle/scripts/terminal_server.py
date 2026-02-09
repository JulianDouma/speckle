#!/usr/bin/env python3
"""
Speckle Terminal Server

WebSocket-based terminal mirroring for subagent processes.
Allows real-time viewing and control of agent terminals from the kanban board.

Architecture:
    ┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
    │   Subagent      │────▶│   PTY Bridge     │────▶│  WebSocket      │
    │   Process       │     │   (this module)  │     │  Server         │
    └─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                              │ WS
                                                   ┌──────────▼────────┐
                                                   │   Kanban Board    │
                                                   │   (xterm.js)      │
                                                   └───────────────────┘

Usage:
    # Start WebSocket server
    python terminal_server.py server --port 8421
    
    # Spawn terminal for a bead
    python terminal_server.py spawn speckle-abc -- claude --task "..."
    
    # List active sessions
    python terminal_server.py list
"""

from __future__ import annotations

import asyncio
import json
import os
import pty
import signal
import struct
import sys
import fcntl
import termios
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Set, Any, List, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime

if TYPE_CHECKING:
    from websockets.server import WebSocketServerProtocol

# Try to import websockets, provide fallback info if not available
try:
    import websockets
    from websockets.server import serve as ws_serve
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False
    ws_serve = None  # type: ignore


# === Configuration ===
DEFAULT_WS_PORT = 8421
TERMINAL_DIR = Path(".speckle/terminals")
HISTORY_LINES = 1000  # Lines of scrollback to keep
MAX_BUFFER_SIZE = 1024 * 1024  # 1MB max buffer
TRIM_BUFFER_SIZE = 512 * 1024  # Trim to 512KB when exceeded


@dataclass
class TerminalSession:
    """Represents a running terminal session for a bead."""
    bead_id: str
    pid: int
    master_fd: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    output_buffer: bytearray = field(default_factory=bytearray)
    subscribers: Set[Any] = field(default_factory=set)
    command: str = ""
    cwd: str = ""
    active: bool = True
    
    def to_dict(self) -> dict:
        return {
            "bead_id": self.bead_id,
            "pid": self.pid,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "command": self.command,
            "cwd": self.cwd,
            "subscribers": len(self.subscribers),
            "buffer_size": len(self.output_buffer),
            "active": self.active,
        }


class TerminalManager:
    """Manages multiple terminal sessions for different beads."""
    
    def __init__(self):
        self.sessions: Dict[str, TerminalSession] = {}
        self.lock = threading.Lock()
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        TERMINAL_DIR.mkdir(parents=True, exist_ok=True)
    
    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        """Set the event loop for async notifications."""
        self._event_loop = loop
    
    def create_session(
        self, 
        bead_id: str, 
        command: List[str], 
        cwd: Optional[str] = None
    ) -> TerminalSession:
        """Create a new terminal session for a bead."""
        if bead_id in self.sessions:
            self.terminate_session(bead_id)
        
        # Create PTY
        master_fd, slave_fd = pty.openpty()
        
        # Set terminal size (80x24 default)
        winsize = struct.pack("HHHH", 24, 80, 0, 0)
        fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)
        
        # Make master non-blocking
        flags = fcntl.fcntl(master_fd, fcntl.F_GETFL)
        fcntl.fcntl(master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        
        # Spawn subprocess
        env = os.environ.copy()
        env["TERM"] = "xterm-256color"
        env["SPECKLE_BEAD_ID"] = bead_id
        env["SPECKLE_TERMINAL"] = "1"
        env["COLORTERM"] = "truecolor"
        
        working_dir = cwd if cwd else os.getcwd()
        
        pid = os.fork()
        if pid == 0:
            # Child process
            os.setsid()
            os.dup2(slave_fd, 0)
            os.dup2(slave_fd, 1)
            os.dup2(slave_fd, 2)
            os.close(master_fd)
            os.close(slave_fd)
            os.chdir(working_dir)
            os.execvpe(command[0], command, env)
        
        # Parent process
        os.close(slave_fd)
        
        session = TerminalSession(
            bead_id=bead_id,
            pid=pid,
            master_fd=master_fd,
            command=" ".join(command),
            cwd=working_dir,
        )
        
        with self.lock:
            self.sessions[bead_id] = session
        
        # Save session info to file
        self._save_session_info(session)
        
        # Start reading thread
        threading.Thread(
            target=self._read_output,
            args=(bead_id,),
            daemon=True,
            name=f"pty-reader-{bead_id}"
        ).start()
        
        return session
    
    def _read_output(self, bead_id: str):
        """Background thread to read PTY output."""
        while bead_id in self.sessions:
            session = self.sessions.get(bead_id)
            if not session or not session.active:
                break
            
            try:
                data = os.read(session.master_fd, 4096)
                if data:
                    session.output_buffer.extend(data)
                    session.last_activity = datetime.utcnow()
                    
                    # Trim buffer if too large
                    if len(session.output_buffer) > MAX_BUFFER_SIZE:
                        session.output_buffer = session.output_buffer[-TRIM_BUFFER_SIZE:]
                    
                    # Save to log file for persistence
                    self._append_to_log(bead_id, data)
                    
                    # Notify subscribers (async)
                    if self._event_loop and session.subscribers:
                        self._event_loop.call_soon_threadsafe(
                            self._schedule_notify, session, data
                        )
            except OSError as e:
                if e.errno == 5:  # EIO - process terminated
                    break
                elif e.errno == 11:  # EAGAIN - no data available
                    time.sleep(0.01)
                else:
                    break
            except Exception:
                time.sleep(0.01)
        
        # Clean up
        self._cleanup_session(bead_id)
    
    def _schedule_notify(self, session: TerminalSession, data: bytes):
        """Schedule notification task."""
        asyncio.create_task(self._notify_subscribers(session, data))
    
    async def _notify_subscribers(self, session: TerminalSession, data: bytes):
        """Send data to all WebSocket subscribers."""
        if not session.subscribers:
            return
        
        message = json.dumps({
            "type": "output",
            "bead_id": session.bead_id,
            "data": data.decode("utf-8", errors="replace"),
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        dead_sockets = []
        for ws in list(session.subscribers):
            try:
                await ws.send(message)
            except Exception:
                dead_sockets.append(ws)
        
        for ws in dead_sockets:
            session.subscribers.discard(ws)
    
    def _append_to_log(self, bead_id: str, data: bytes):
        """Append output to log file for persistence."""
        log_file = TERMINAL_DIR / f"{bead_id}.log"
        try:
            with open(log_file, "ab") as f:
                f.write(data)
        except Exception:
            pass
    
    def write_to_session(self, bead_id: str, data: str) -> bool:
        """Write input to a terminal session."""
        session = self.sessions.get(bead_id)
        if not session or not session.active:
            return False
        
        try:
            os.write(session.master_fd, data.encode("utf-8"))
            return True
        except OSError:
            return False
    
    def resize_session(self, bead_id: str, rows: int, cols: int) -> bool:
        """Resize terminal window."""
        session = self.sessions.get(bead_id)
        if not session or not session.active:
            return False
        
        try:
            winsize = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(session.master_fd, termios.TIOCSWINSZ, winsize)
            return True
        except OSError:
            return False
    
    def terminate_session(self, bead_id: str) -> bool:
        """Terminate a terminal session."""
        session = self.sessions.get(bead_id)
        if not session:
            return False
        
        session.active = False
        
        try:
            os.kill(session.pid, signal.SIGTERM)
            # Give it a moment to clean up
            time.sleep(0.5)
            try:
                os.kill(session.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        except ProcessLookupError:
            pass
        
        self._cleanup_session(bead_id)
        return True
    
    def send_signal(self, bead_id: str, sig: int) -> bool:
        """Send a signal to terminal process."""
        session = self.sessions.get(bead_id)
        if not session or not session.active:
            return False
        
        try:
            os.kill(session.pid, sig)
            return True
        except ProcessLookupError:
            return False
    
    def get_session(self, bead_id: str) -> Optional[TerminalSession]:
        """Get session by bead ID."""
        return self.sessions.get(bead_id)
    
    def get_buffer(self, bead_id: str) -> bytes:
        """Get output buffer for session."""
        session = self.sessions.get(bead_id)
        if session:
            return bytes(session.output_buffer)
        
        # Try to load from log file if no active session
        log_file = TERMINAL_DIR / f"{bead_id}.log"
        if log_file.exists():
            try:
                # Return last 512KB of log
                with open(log_file, "rb") as f:
                    f.seek(0, 2)  # End of file
                    size = f.tell()
                    if size > TRIM_BUFFER_SIZE:
                        f.seek(-TRIM_BUFFER_SIZE, 2)
                    else:
                        f.seek(0)
                    return f.read()
            except Exception:
                pass
        
        return b""
    
    def list_sessions(self) -> List[dict]:
        """List all active sessions."""
        return [s.to_dict() for s in self.sessions.values() if s.active]
    
    def subscribe(self, bead_id: str, websocket: Any) -> bool:
        """Subscribe a websocket to a session."""
        session = self.sessions.get(bead_id)
        if session and session.active:
            session.subscribers.add(websocket)
            return True
        return False
    
    def unsubscribe(self, bead_id: str, websocket: Any):
        """Unsubscribe a websocket from a session."""
        session = self.sessions.get(bead_id)
        if session:
            session.subscribers.discard(websocket)
    
    def _save_session_info(self, session: TerminalSession):
        """Save session info to file for external tools."""
        info_file = TERMINAL_DIR / f"{session.bead_id}.json"
        try:
            with open(info_file, "w") as f:
                json.dump(session.to_dict(), f, indent=2)
        except Exception:
            pass
    
    def _cleanup_session(self, bead_id: str):
        """Clean up a terminated session."""
        with self.lock:
            session = self.sessions.pop(bead_id, None)
        
        if session:
            session.active = False
            try:
                os.close(session.master_fd)
            except OSError:
                pass
            
            # Remove info file (keep log file for history)
            info_file = TERMINAL_DIR / f"{bead_id}.json"
            try:
                info_file.unlink()
            except FileNotFoundError:
                pass
            
            # Notify subscribers of disconnect
            if self._event_loop and session.subscribers:
                for ws in session.subscribers:
                    try:
                        self._event_loop.call_soon_threadsafe(
                            lambda w=ws: asyncio.create_task(
                                w.send(json.dumps({
                                    "type": "terminated",
                                    "bead_id": bead_id,
                                }))
                            )
                        )
                    except Exception:
                        pass


# Global terminal manager instance
terminal_manager = TerminalManager()


async def handle_websocket(websocket: Any, path: str = ""):
    """Handle WebSocket connections."""
    subscribed_beads: Set[str] = set()
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type")
                bead_id = data.get("bead_id", "")
                
                if msg_type == "subscribe":
                    if bead_id:
                        if terminal_manager.subscribe(bead_id, websocket):
                            subscribed_beads.add(bead_id)
                            # Send current buffer
                            buffer = terminal_manager.get_buffer(bead_id)
                            await websocket.send(json.dumps({
                                "type": "buffer",
                                "bead_id": bead_id,
                                "data": buffer.decode("utf-8", errors="replace"),
                            }))
                            await websocket.send(json.dumps({
                                "type": "subscribed",
                                "bead_id": bead_id,
                            }))
                        else:
                            await websocket.send(json.dumps({
                                "type": "error",
                                "message": f"No active terminal session for {bead_id}",
                            }))
                
                elif msg_type == "unsubscribe":
                    if bead_id:
                        terminal_manager.unsubscribe(bead_id, websocket)
                        subscribed_beads.discard(bead_id)
                
                elif msg_type == "input":
                    if bead_id and "data" in data:
                        terminal_manager.write_to_session(bead_id, data["data"])
                
                elif msg_type == "resize":
                    if bead_id:
                        rows = data.get("rows", 24)
                        cols = data.get("cols", 80)
                        terminal_manager.resize_session(bead_id, rows, cols)
                
                elif msg_type == "signal":
                    if bead_id:
                        sig_name = data.get("signal", "SIGINT")
                        sig = getattr(signal, sig_name, signal.SIGINT)
                        terminal_manager.send_signal(bead_id, sig)
                        await websocket.send(json.dumps({
                            "type": "signal_sent",
                            "bead_id": bead_id,
                            "signal": sig_name,
                        }))
                
                elif msg_type == "terminate":
                    if bead_id:
                        success = terminal_manager.terminate_session(bead_id)
                        await websocket.send(json.dumps({
                            "type": "terminated" if success else "error",
                            "bead_id": bead_id,
                            "message": "Session terminated" if success else "Session not found",
                        }))
                
                elif msg_type == "list":
                    sessions = terminal_manager.list_sessions()
                    await websocket.send(json.dumps({
                        "type": "sessions",
                        "sessions": sessions,
                    }))
                
                elif msg_type == "spawn":
                    # Spawn new terminal for a bead
                    if bead_id and "command" in data:
                        command = data["command"]
                        if isinstance(command, str):
                            command = ["bash", "-c", command]
                        cwd = data.get("cwd")
                        session = terminal_manager.create_session(bead_id, command, cwd)
                        await websocket.send(json.dumps({
                            "type": "spawned",
                            "session": session.to_dict(),
                        }))
                
                elif msg_type == "history":
                    # Get historical output
                    if bead_id:
                        buffer = terminal_manager.get_buffer(bead_id)
                        await websocket.send(json.dumps({
                            "type": "history",
                            "bead_id": bead_id,
                            "data": buffer.decode("utf-8", errors="replace"),
                        }))
                
                elif msg_type == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))
                
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON",
                }))
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    
    finally:
        # Unsubscribe from all on disconnect
        for bead_id in subscribed_beads:
            terminal_manager.unsubscribe(bead_id, websocket)


async def start_websocket_server(host: str = "localhost", port: int = DEFAULT_WS_PORT):
    """Start the WebSocket server."""
    if not HAS_WEBSOCKETS or ws_serve is None:
        print("Error: websockets library required. Install with: pip install websockets")
        sys.exit(1)
    
    # Set event loop for terminal manager
    terminal_manager.set_event_loop(asyncio.get_event_loop())
    
    print(f"🔌 Starting terminal WebSocket server on ws://{host}:{port}")
    print(f"📁 Terminal logs: {TERMINAL_DIR.absolute()}")
    
    async with ws_serve(handle_websocket, host, port):
        await asyncio.Future()  # Run forever


def spawn_with_terminal(
    bead_id: str, 
    command: List[str], 
    cwd: Optional[str] = None
) -> TerminalSession:
    """
    Spawn a command with terminal capture.
    
    Usage:
        session = spawn_with_terminal("speckle-abc", ["claude", "--task", "..."])
    """
    return terminal_manager.create_session(bead_id, command, cwd)


# === CLI Interface ===

def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Speckle Terminal Server - Real-time terminal mirroring for subagents"
    )
    subparsers = parser.add_subparsers(dest="command")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start WebSocket server")
    server_parser.add_argument("--host", default="localhost", help="Host to bind (default: localhost)")
    server_parser.add_argument("--port", type=int, default=DEFAULT_WS_PORT, help=f"Port to bind (default: {DEFAULT_WS_PORT})")
    
    # Spawn command
    spawn_parser = subparsers.add_parser("spawn", help="Spawn terminal for bead")
    spawn_parser.add_argument("bead_id", help="Bead ID")
    spawn_parser.add_argument("cmd", nargs="+", help="Command to run")
    spawn_parser.add_argument("--cwd", help="Working directory")
    
    # List command
    subparsers.add_parser("list", help="List active sessions")
    
    # Terminate command
    term_parser = subparsers.add_parser("terminate", help="Terminate session")
    term_parser.add_argument("bead_id", help="Bead ID")
    
    # History command
    hist_parser = subparsers.add_parser("history", help="Show terminal history")
    hist_parser.add_argument("bead_id", help="Bead ID")
    hist_parser.add_argument("--lines", type=int, default=100, help="Number of lines")
    
    args = parser.parse_args()
    
    if args.command == "server":
        try:
            asyncio.run(start_websocket_server(args.host, args.port))
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
    
    elif args.command == "spawn":
        session = spawn_with_terminal(args.bead_id, args.cmd, args.cwd)
        print(json.dumps(session.to_dict(), indent=2))
        # Keep running to maintain session
        try:
            while args.bead_id in terminal_manager.sessions:
                time.sleep(1)
        except KeyboardInterrupt:
            terminal_manager.terminate_session(args.bead_id)
            print(f"\n👋 Session terminated: {args.bead_id}")
    
    elif args.command == "list":
        sessions = terminal_manager.list_sessions()
        if sessions:
            print(json.dumps(sessions, indent=2))
        else:
            print("No active terminal sessions")
    
    elif args.command == "terminate":
        if terminal_manager.terminate_session(args.bead_id):
            print(f"✓ Terminated session: {args.bead_id}")
        else:
            print(f"✗ No session found: {args.bead_id}")
            sys.exit(1)
    
    elif args.command == "history":
        buffer = terminal_manager.get_buffer(args.bead_id)
        if buffer:
            # Get last N lines
            lines = buffer.decode("utf-8", errors="replace").split("\n")
            for line in lines[-args.lines:]:
                print(line)
        else:
            print(f"No history for: {args.bead_id}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
