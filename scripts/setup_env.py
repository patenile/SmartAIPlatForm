#!/usr/bin/env python3
"""
setup_env.py: Ensures .venv exists, creates it with python3.12 if missing, and checks/installs required packages from requirements.txt.
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path
import argparse

# Debug flag: set via env or CLI
DEBUG = os.environ.get('SMARTAI_DEBUG', '0') == '1'
def debug(msg):
    if DEBUG:
        print(f'[DEBUG] {msg}')

# Project root is the parent of this script's directory
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
VENV_PATH = str(PROJECT_ROOT / '.venv')
REQUIREMENTS = str(PROJECT_ROOT / 'requirements.txt')

def create_venv():
    """Create a new virtual environment at VENV_PATH using python3.12."""
    python_bin = find_python312()
    if not python_bin:
        print("ERROR: python3.12 not found. Please install Python 3.12 and try again.")
        sys.exit(1)
    debug(f"Creating .venv at {VENV_PATH} with {python_bin}...")
    try:
        debug("Running: python -m venv ...")
        subprocess.check_call([python_bin, '-m', 'venv', VENV_PATH])
        debug(".venv created.")
    except Exception as e:
        debug(f"Error during venv creation: {e}")
        raise

def get_installed_packages():
    """Return a dict of normalized package names to installed package specifiers in .venv."""
    pip = os.path.join(VENV_PATH, 'bin', 'pip')
    pkgs = {}
    try:
        out = subprocess.check_output([pip, 'freeze'], encoding='utf-8')
        for line in out.splitlines():
            orig = line.strip()
            if not orig or orig.startswith('#'):
                continue
            pkg = orig.split('==')[0].split('>=')[0].split('<=')[0].lower()
            if '[' in pkg and ']' in pkg:
                pkg = pkg.split('[')[0]
            norm = pkg.replace('-', '').replace('_', '')
            pkgs[norm] = pkg
    except Exception:
        pass
    return pkgs

def venv_exists():
    """Return True if .venv directory exists and contains a Python executable."""
    venv_dir = Path(VENV_PATH)
    python_bin = venv_dir / 'bin' / 'python'
    return venv_dir.is_dir() and python_bin.exists()

def find_python312():
    # Allow override by env var
    override = os.environ.get('PYTHON312_BIN')
    if override and shutil.which(override):
        return override
    # Try common names
    for name in ['python3.12', 'python312', 'python']:
        path = shutil.which(name)
        if path:
            # Optionally check version here if needed
            return path
    return None


def get_required_packages():
    if not os.path.exists(REQUIREMENTS):
        print(f"ERROR: {REQUIREMENTS} not found.")
        sys.exit(1)
    with open(REQUIREMENTS) as f:
        pkgs = {}
        for line in f:
            orig_line = line.strip()
            line = orig_line
            if not line or line.startswith('#'):
                continue
            # Handle extras: passlib[bcrypt]
            pkg = line.split('==')[0].split('>=')[0].split('<=')[0].lower()
            # Strip extras if present
            if '[' in pkg and ']' in pkg:
                pkg = pkg.split('[')[0]
            norm = pkg.replace('-', '').replace('_', '')
            pkgs[norm] = orig_line
        return pkgs


def install_missing_packages():
    pip = os.path.join(VENV_PATH, 'bin', 'pip')
    # Always upgrade pip first
    debug('Upgrading pip...')
    try:
        debug(f"Running: {pip} install --upgrade pip")
        subprocess.check_call([pip, 'install', '--upgrade', 'pip'])
        debug("pip upgraded.")
    except Exception as e:
        debug(f"Error upgrading pip: {e}")
        raise
    required = get_required_packages()  # dict: norm -> original req line
    installed = get_installed_packages()  # dict: norm -> installed name
    missing = [required[n] for n in required if n not in installed]
    GREEN = '\033[92m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    if not missing:
        print(f"{BOLD}{GREEN}All required packages are already installed.{RESET}")
        return
    debug(f"Installing missing packages: {', '.join(missing)}")
    try:
        debug(f"Running: {pip} install -r {REQUIREMENTS}")
        subprocess.check_call([pip, 'install', '-r', REQUIREMENTS])
        debug("Requirements installed.")
    except Exception as e:
        debug(f"Error installing requirements: {e}")
        raise
    # Re-check after install
    installed = get_installed_packages()
    still_missing = [required[n] for n in required if n not in installed]
    if still_missing:
        print(f"{BOLD}{RED}ERROR: The following packages are still missing after install:{RESET} {', '.join(still_missing)}")
        print(f"{RED}If you are using extras (e.g., passlib[bcrypt]), ensure your pip version is up to date and try again.{RESET}")
        sys.exit(1)
    print(f"{BOLD}{GREEN}All required packages installed.{RESET}")

def interactive_cli():
    print("SmartAIPlatForm setup_env.py interactive mode. Type 'help' for options, 'exit' to quit.")
    while True:
        try:
            cmd = input("setup_env> ").strip().lower()
        except EOFError:
            print("\nInput error (EOF). Printing help and exiting.")
            print("Commands: help, exit, setup, status")
            print("Exiting interactive mode.")
            break
        if cmd in ("exit", "quit"):
            print("Exiting interactive mode.")
            break
        elif cmd == "help":
            print("Commands: help, exit, setup, status")
        elif cmd == "setup":
            first_time = False
            if not venv_exists():
                create_venv()
                first_time = True
            else:
                print('.venv already exists.')
            install_missing_packages()
            GREEN = '\033[92m'
            BOLD = '\033[1m'
            RESET = '\033[0m'
            print(f"{BOLD}{GREEN}Environment setup complete.{RESET}")
            if first_time:
                BOLD = '\033[1m'
                YELLOW = '\033[93m'
                RESET = '\033[0m'
                print(f"\n{BOLD}{YELLOW}IMPORTANT: To activate your new environment, run:{RESET}")
                print(f"{BOLD}{YELLOW}  source .venv/bin/activate  {RESET}")
                print(f"{BOLD}After activation, use '.venv/bin/python' or 'python' (if shell is activated) to run project scripts.{RESET}")
        elif cmd == "status":
            print(".venv exists:" , venv_exists())
            if venv_exists():
                print("Installed packages:")
                pkgs = get_installed_packages()
                for pkg in pkgs.values():
                    print("-", pkg)
            else:
                print("No .venv found.")
        else:
            print("Unknown command. Type 'help'.")

def main():
    parser = argparse.ArgumentParser(description="SmartAIPlatForm setup_env.py")
    parser.add_argument("command", nargs="?", choices=["setup", "status", "info", "version", "reset", "diagnostics"], help="Action to perform")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    global DEBUG
    DEBUG = args.debug or os.environ.get('SMARTAI_DEBUG', '0') == '1'
    if args.command is None:
        interactive_cli()
        return
    debug('Debug mode enabled via CLI argument.')
    # Only run main logic for valid commands
    first_time = False
    if args.command == "setup":
        if not venv_exists():
            create_venv()
            first_time = True
        else:
            print('.venv already exists.')
        install_missing_packages()
        GREEN = '\033[92m'
        BOLD = '\033[1m'
        RESET = '\033[0m'
        print(f"{BOLD}{GREEN}Environment setup complete.{RESET}")
        if first_time:
            BOLD = '\033[1m'
            YELLOW = '\033[93m'
            RESET = '\033[0m'
            print(f"\n{BOLD}{YELLOW}IMPORTANT: To activate your new environment, run:{RESET}")
            print(f"{BOLD}{YELLOW}  source .venv/bin/activate  {RESET}")
            print(f"{BOLD}After activation, use '.venv/bin/python' or 'python' (if shell is activated) to run project scripts.{RESET}")
    elif args.command == "status":
        print(".venv exists:" , venv_exists())
        if venv_exists():
            print("Installed packages:")
            pkgs = get_installed_packages()
            for pkg in pkgs.values():
                print("-", pkg)
        else:
            print("No .venv found.")
    elif args.command in ["info", "version", "reset", "diagnostics"]:
        print(f"Command '{args.command}' not yet implemented in main(). Use interactive mode.")
    else:
        print("Usage: setup_env.py [setup|status|info|version|reset|diagnostics] [--debug]")
        sys.exit(0)

if __name__ == '__main__':
    main()
