#!/usr/bin/env python3
"""
Speckle CLI - Unified command-line interface for Speckle tools

Usage:
    speckle board [--port PORT]     Start kanban board server
    speckle doctor [--fix]          Run diagnostic checks
    speckle status                  Show feature progress (via bd)
    speckle sync                    Sync beads with git (via bd)
    speckle --help                  Show this help message
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def get_speckle_root() -> Path:
    """Find the .speckle directory, searching up from cwd."""
    current = Path.cwd()
    while current != current.parent:
        if (current / '.speckle').is_dir():
            return current / '.speckle'
        current = current.parent
    # Fallback to cwd/.speckle
    return Path.cwd() / '.speckle'


def cmd_board(args):
    """Start the kanban board server."""
    speckle_root = get_speckle_root()
    board_script = speckle_root / 'scripts' / 'board.py'
    
    if not board_script.exists():
        print(f"Error: board.py not found at {board_script}", file=sys.stderr)
        return 1
    
    cmd = [sys.executable, str(board_script)]
    if args.port:
        cmd.extend(['--port', str(args.port)])
    if args.no_browser:
        cmd.append('--no-browser')
    
    return subprocess.call(cmd)


def cmd_doctor(args):
    """Run diagnostic checks."""
    speckle_root = get_speckle_root()
    doctor_script = speckle_root / 'scripts' / 'doctor.py'
    
    if not doctor_script.exists():
        print(f"Error: doctor.py not found at {doctor_script}", file=sys.stderr)
        return 1
    
    cmd = [sys.executable, str(doctor_script)]
    if args.fix:
        cmd.append('--fix')
    if args.verbose:
        cmd.append('--verbose')
    
    return subprocess.call(cmd)


def cmd_status(args):
    """Show feature progress via beads."""
    cmd = ['bd', 'list']
    if args.all:
        cmd.append('--all')
    return subprocess.call(cmd)


def cmd_sync(args):
    """Sync beads with git."""
    return subprocess.call(['bd', 'sync'])


def cmd_ready(args):
    """Show ready work items."""
    return subprocess.call(['bd', 'ready'])


def cmd_version(args):
    """Show version information."""
    version_file = get_speckle_root().parent / 'VERSION'
    if version_file.exists():
        version = version_file.read_text().strip()
    else:
        version = "1.2.0"  # Default
    print(f"speckle {version}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog='speckle',
        description='Speckle - AI-powered development workflow tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Commands:
  board       Start the kanban board web interface
  doctor      Run diagnostic checks on your Speckle installation
  status      Show current work status (via beads)
  sync        Sync beads issues with git
  ready       Show available work items
  version     Show version information

Examples:
  speckle board                    # Start board on default port 8420
  speckle board --port 3000        # Start board on port 3000
  speckle doctor --fix             # Run diagnostics and fix issues
  speckle status --all             # Show all issues including closed

For Claude commands, use:
  /speckle.implement               # Implement next task
  /speckle.progress "note"         # Add progress note
'''
    )
    
    parser.add_argument('--version', '-v', action='store_true', 
                        help='Show version and exit')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # board subcommand
    board_parser = subparsers.add_parser('board', help='Start kanban board server')
    board_parser.add_argument('--port', '-p', type=int, default=8420,
                              help='Port to run server on (default: 8420)')
    board_parser.add_argument('--no-browser', action='store_true',
                              help='Do not open browser automatically')
    board_parser.set_defaults(func=cmd_board)
    
    # doctor subcommand
    doctor_parser = subparsers.add_parser('doctor', help='Run diagnostic checks')
    doctor_parser.add_argument('--fix', '-f', action='store_true',
                               help='Attempt to fix issues automatically')
    doctor_parser.add_argument('--verbose', '-v', action='store_true',
                               help='Show detailed output')
    doctor_parser.set_defaults(func=cmd_doctor)
    
    # status subcommand
    status_parser = subparsers.add_parser('status', help='Show work status')
    status_parser.add_argument('--all', '-a', action='store_true',
                               help='Show all issues including closed')
    status_parser.set_defaults(func=cmd_status)
    
    # sync subcommand
    sync_parser = subparsers.add_parser('sync', help='Sync beads with git')
    sync_parser.set_defaults(func=cmd_sync)
    
    # ready subcommand
    ready_parser = subparsers.add_parser('ready', help='Show available work')
    ready_parser.set_defaults(func=cmd_ready)
    
    # version subcommand
    version_parser = subparsers.add_parser('version', help='Show version')
    version_parser.set_defaults(func=cmd_version)
    
    args = parser.parse_args()
    
    if args.version:
        return cmd_version(args)
    
    if not args.command:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
