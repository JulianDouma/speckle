#!/usr/bin/env python3
"""
Speckle Doctor - Diagnostic tool for Speckle installation

Checks:
- Prerequisites (git, gh, bd, specify)
- Directory structure (.speckle/, .claude/, .beads/)
- File permissions and integrity
- Configuration validity
- Integration health (beads, git)
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Tuple, List, Optional


# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color
    
    @classmethod
    def disable(cls):
        """Disable colors for non-tty output."""
        cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = cls.NC = ''


# Detect if we should use colors
if not sys.stdout.isatty():
    Colors.disable()


def success(msg: str) -> str:
    return f"  {Colors.GREEN}✅{Colors.NC} {msg}"


def warning(msg: str) -> str:
    return f"  {Colors.YELLOW}⚠️{Colors.NC}  {msg}"


def error(msg: str) -> str:
    return f"  {Colors.RED}❌{Colors.NC} {msg}"


def info(msg: str) -> str:
    return f"  {Colors.BLUE}ℹ️{Colors.NC}  {msg}"


def header(msg: str) -> str:
    return f"\n{'═' * 60}\n{msg}\n{'═' * 60}\n"


def run_command(cmd: List[str], timeout: int = 10) -> Tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, '', 'Command timed out'
    except FileNotFoundError:
        return -1, '', 'Command not found'


def check_command(name: str) -> Tuple[bool, str]:
    """Check if a command exists and return its version."""
    path = shutil.which(name)
    if not path:
        return False, ''
    
    # Try to get version
    version_flags = ['--version', '-v', '-V', 'version']
    for flag in version_flags:
        code, stdout, _ = run_command([name, flag])
        if code == 0 and stdout:
            # Get first line only
            return True, stdout.split('\n')[0]
    
    return True, 'installed'


class Doctor:
    def __init__(self, fix_mode: bool = False, verbose: bool = False):
        self.fix_mode = fix_mode
        self.verbose = verbose
        self.issues = 0
        self.warnings = 0
        self.root = Path.cwd()
    
    def run(self) -> int:
        """Run all diagnostic checks."""
        print()
        print("════════════════════════════════════════════════════════════")
        print("🩺 Speckle Doctor")
        print("════════════════════════════════════════════════════════════")
        print()
        print("Running diagnostics...")
        if self.fix_mode:
            print(f"{Colors.YELLOW}🔧 Fix mode enabled{Colors.NC}")
        print()
        
        self.check_prerequisites()
        self.check_directory_structure()
        self.check_scripts()
        self.check_commands()
        self.check_git_integration()
        self.check_beads_integration()
        self.print_summary()
        self.print_recommendations()
        
        return 1 if self.issues > 0 else 0
    
    def check_prerequisites(self):
        """Check required and optional tools."""
        print(header("📦 Prerequisites"))
        
        # git (required)
        found, version = check_command('git')
        if found:
            print(success(f"git: {version}"))
        else:
            print(error("git: NOT FOUND"))
            print("     → Install from https://git-scm.com/downloads")
            self.issues += 1
        
        # gh (recommended)
        found, version = check_command('gh')
        if found:
            print(success(f"gh: {version}"))
            # Check auth
            code, _, _ = run_command(['gh', 'auth', 'status'])
            if code == 0:
                print("     └─ Authenticated")
            else:
                print("     └─ ⚠️  Not authenticated (run: gh auth login)")
                self.warnings += 1
        else:
            print(warning("gh: NOT FOUND (recommended)"))
            print("     → Install from https://cli.github.com")
            self.warnings += 1
        
        # bd (recommended)
        found, version = check_command('bd')
        if found:
            print(success(f"bd: {version}"))
        else:
            print(warning("bd: NOT FOUND (recommended)"))
            print("     → Install from https://github.com/steveyegge/beads")
            self.warnings += 1
        
        # specify (optional)
        found, _ = check_command('specify')
        if found:
            print(success("specify: installed"))
        else:
            print(info("specify: NOT FOUND (optional)"))
            print("     → Install from https://github.com/github/spec-kit")
        
        # jq (recommended for JSON operations)
        found, version = check_command('jq')
        if found:
            print(success(f"jq: {version}"))
        else:
            print(warning("jq: NOT FOUND (recommended for JSON operations)"))
            self.warnings += 1
        
        # Python version
        print(f"\n  Python: {sys.version.split()[0]}")
        print(f"  Shell: {os.environ.get('SHELL', 'unknown')}")
    
    def check_directory_structure(self):
        """Check required directories exist."""
        print(header("📁 Directory Structure"))
        
        # .speckle/
        speckle_dir = self.root / '.speckle'
        if speckle_dir.is_dir():
            print(success(".speckle/"))
            
            for subdir in ['scripts', 'templates', 'formulas']:
                subpath = speckle_dir / subdir
                if subpath.is_dir():
                    file_count = len(list(subpath.iterdir()))
                    print(f"     └─ {subdir}/ ({file_count} files)")
                else:
                    print(f"     └─ {Colors.YELLOW}⚠️{Colors.NC}  {subdir}/ MISSING")
                    self.warnings += 1
                    if self.fix_mode:
                        subpath.mkdir(parents=True, exist_ok=True)
                        print("        → Created")
        else:
            print(error(".speckle/ NOT FOUND"))
            print("     → Run install.sh to set up Speckle")
            self.issues += 1
            if self.fix_mode:
                for subdir in ['scripts', 'templates', 'formulas']:
                    (speckle_dir / subdir).mkdir(parents=True, exist_ok=True)
                print("     → Created directory structure")
        
        # .claude/commands/
        claude_dir = self.root / '.claude' / 'commands'
        if claude_dir.is_dir():
            speckle_cmds = list(claude_dir.glob('speckle*.md'))
            print(success(f".claude/commands/ ({len(speckle_cmds)} speckle commands)"))
        else:
            print(warning(".claude/commands/ NOT FOUND"))
            self.warnings += 1
            if self.fix_mode:
                claude_dir.mkdir(parents=True, exist_ok=True)
                print("     → Created")
        
        # .beads/
        beads_dir = self.root / '.beads'
        if beads_dir.is_dir():
            print(success(".beads/"))
            
            config = beads_dir / 'config.toml'
            if config.exists():
                print("     └─ config.toml exists")
            else:
                print("     └─ ⚠️  config.toml MISSING (run: bd init)")
                self.warnings += 1
            
            formulas_dir = beads_dir / 'formulas'
            if formulas_dir.is_dir():
                formula_count = len(list(formulas_dir.glob('*.toml')))
                print(f"     └─ formulas/ ({formula_count} formulas)")
        else:
            print(warning(".beads/ NOT FOUND"))
            print("     → Run: bd init")
            self.warnings += 1
            if self.fix_mode:
                code, _, _ = run_command(['bd', 'init'])
                if code == 0:
                    print("     → Initialized beads")
        
        # specs/
        specs_dir = self.root / 'specs'
        if specs_dir.is_dir():
            spec_count = len([d for d in specs_dir.iterdir() if d.is_dir()])
            print(success(f"specs/ ({spec_count} features)"))
        else:
            print(info("specs/ NOT FOUND (created on first feature)"))
    
    def check_scripts(self):
        """Check helper scripts exist and are valid."""
        print(header("🔧 Scripts & Helpers"))
        
        scripts_dir = self.root / '.speckle' / 'scripts'
        expected = ['common.sh', 'comments.sh', 'labels.sh', 'epics.sh', 'board.py', 'doctor.py']
        
        for script_name in expected:
            script_path = scripts_dir / script_name
            if script_path.exists():
                is_executable = os.access(script_path, os.X_OK)
                if is_executable or script_name.endswith('.py'):
                    print(success(f"{script_name}" + (" (executable)" if is_executable else "")))
                else:
                    print(warning(f"{script_name} (not executable)"))
                    self.warnings += 1
                    if self.fix_mode:
                        script_path.chmod(script_path.stat().st_mode | 0o111)
                        print("     → Fixed permissions")
                
                # Syntax check for bash scripts
                if self.verbose and script_name.endswith('.sh'):
                    code, _, stderr = run_command(['bash', '-n', str(script_path)])
                    if code == 0:
                        print("     └─ Syntax OK")
                    else:
                        print(f"     └─ {Colors.RED}❌{Colors.NC} Syntax error!")
                        self.issues += 1
            else:
                print(warning(f"{script_name} MISSING"))
                self.warnings += 1
    
    def check_commands(self):
        """Check Claude command files exist."""
        print(header("📋 Speckle Commands"))
        
        commands_dir = self.root / '.claude' / 'commands'
        expected = [
            ('speckle.sync.md', 'Sync tasks with beads'),
            ('speckle.implement.md', 'Implement tasks'),
            ('speckle.status.md', 'Show progress'),
            ('speckle.progress.md', 'Add progress notes'),
            ('speckle.bugfix.md', 'Bugfix workflow'),
            ('speckle.hotfix.md', 'Hotfix workflow'),
            ('speckle.doctor.md', 'This diagnostic'),
            ('speckle.board.md', 'Kanban board'),
        ]
        
        for cmd_file, description in expected:
            cmd_path = commands_dir / cmd_file
            if cmd_path.exists():
                print(success(cmd_file))
                if self.verbose:
                    print(f"     └─ {description}")
            else:
                print(warning(f"{cmd_file} MISSING"))
                self.warnings += 1
    
    def check_git_integration(self):
        """Check git repository status."""
        print(header("🔗 Git Integration"))
        
        git_dir = self.root / '.git'
        if git_dir.is_dir():
            print(success("Git repository detected"))
            
            # Current branch
            code, branch, _ = run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
            if code == 0:
                print(f"     └─ Branch: {branch}")
            
            # Remote
            code, remote, _ = run_command(['git', 'remote', 'get-url', 'origin'])
            if code == 0:
                print(f"     └─ Remote: {remote}")
            else:
                print("     └─ ⚠️  No remote configured")
                self.warnings += 1
            
            # Working tree status
            code1, _, _ = run_command(['git', 'diff', '--quiet'])
            code2, _, _ = run_command(['git', 'diff', '--cached', '--quiet'])
            if code1 == 0 and code2 == 0:
                print("     └─ Working tree clean")
            else:
                code, stdout, _ = run_command(['git', 'status', '--porcelain'])
                if code == 0:
                    changes = len(stdout.split('\n')) if stdout else 0
                    print(f"     └─ ℹ️  {changes} uncommitted change(s)")
        else:
            print(warning("Not a git repository"))
            print("     → Run: git init")
            self.warnings += 1
    
    def check_beads_integration(self):
        """Check beads is working."""
        print(header("📝 Beads Integration"))
        
        beads_dir = self.root / '.beads'
        if not beads_dir.is_dir():
            print(info("Beads not configured"))
            return
        
        found, _ = check_command('bd')
        if not found:
            print(warning("bd command not available"))
            return
        
        code, stdout, _ = run_command(['bd', 'list'])
        if code == 0:
            # Count speckle issues
            issues = stdout.count('speckle-') if stdout else 0
            print(success("Beads operational"))
            print(f"     └─ {issues} Speckle issue(s)")
            
            # Count by status
            for status in ['open', 'in_progress']:
                code, out, _ = run_command(['bd', 'list', '--status', status])
                if code == 0:
                    count = out.count('speckle-') if out else 0
                    label = "In progress" if status == 'in_progress' else status.capitalize()
                    if status == 'in_progress' and count > 3:
                        print(f"     └─ ⚠️  Many in-progress issues ({count})")
                        self.warnings += 1
                    else:
                        print(f"     └─ {label}: {count}")
        else:
            print(warning("Beads command failed"))
            print("     → Check .beads/config.toml")
            self.warnings += 1
    
    def print_summary(self):
        """Print diagnostic summary."""
        print(header("📊 Diagnosis Summary"))
        
        if self.issues == 0 and self.warnings == 0:
            print(f"  🎉 All checks passed! Speckle is healthy.")
        elif self.issues == 0:
            print(success("No critical issues found"))
            print(warning(f"{self.warnings} warning(s) - optional improvements available"))
        else:
            print(error(f"{self.issues} critical issue(s) found"))
            print(warning(f"{self.warnings} warning(s)"))
            print()
            print("  Run with --fix to attempt automatic repairs:")
            print("    speckle doctor --fix")
        
        print()
        print("═" * 60)
    
    def print_recommendations(self):
        """Print context-specific recommendations."""
        print()
        print("💡 Recommendations")
        print()
        
        beads_dir = self.root / '.beads'
        found_bd, _ = check_command('bd')
        if not beads_dir.is_dir() or not found_bd:
            print("  → Install Beads for issue tracking:")
            print("    https://github.com/steveyegge/beads")
            print()
        
        found_gh, _ = check_command('gh')
        if not found_gh:
            print("  → Install GitHub CLI for better integration:")
            print("    https://cli.github.com")
            print()
        
        specs_dir = self.root / 'specs'
        if not specs_dir.is_dir():
            print("  → Create your first feature spec:")
            print("    /speckit.specify \"My feature idea\"")
            print()
        
        print("📖 Documentation: https://github.com/JulianDouma/Speckle")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Speckle Doctor - Diagnostic tool'
    )
    parser.add_argument('--fix', '-f', action='store_true',
                        help='Attempt to fix issues automatically')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed output')
    
    args = parser.parse_args()
    
    doctor = Doctor(fix_mode=args.fix, verbose=args.verbose)
    return doctor.run()


if __name__ == '__main__':
    sys.exit(main())
