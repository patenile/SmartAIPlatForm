#!/usr/bin/env python3
"""
setup_env.py: Ensures .venv exists, creates it with python3.12 if missing, and checks/installs required packages from requirements.txt.
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

# Project root is the parent of this script's directory
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
VENV_PATH = str(PROJECT_ROOT / '.venv')
REQUIREMENTS = str(PROJECT_ROOT / 'requirements.txt')

def find_python312():
    # Allow override by env var
    override = os.environ.get('PYTHON312_BIN')
    if override and shutil.which(override):
        return override
    # Try common names
    for name in ['python3.12', 'python312', 'python']:  # last fallback
        path = shutil.which(name)
        if path:
            # Check version
            try:
                out = subprocess.check_output([path, '--version'], encoding='utf-8')
                if out.startswith('Python 3.12'):
                    return path
            except Exception:
                continue
    print('ERROR: python3.12 not found in PATH. Please install Python 3.12+ or set PYTHON312_BIN.')
    sys.exit(1)


def venv_exists():
    return os.path.isdir(VENV_PATH) and os.path.isfile(os.path.join(VENV_PATH, 'bin', 'activate'))

def create_venv():
    python_bin = find_python312()
    print(f'Creating .venv with {python_bin}...')
    subprocess.check_call([python_bin, '-m', 'venv', VENV_PATH])
    print('Created .venv')


def get_installed_packages():
    pip = os.path.join(VENV_PATH, 'bin', 'pip')
    out = subprocess.check_output([pip, 'freeze'], encoding='utf-8')
    pkgs = {}
    for line in out.splitlines():
        if '==' in line:
            pkg = line.split('==')[0].lower()
            orig = pkg
            # Strip extras if present
            if '[' in pkg and ']' in pkg:
                pkg = pkg.split('[')[0]
            norm = pkg.replace('-', '').replace('_', '')
            pkgs[norm] = orig
        # Ignore lines without '==' (not a package)
    return pkgs


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
    print('Upgrading pip...')
    subprocess.check_call([pip, 'install', '--upgrade', 'pip'])
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
    print(f"{BOLD}Installing missing packages:{RESET} {', '.join(missing)}")
    subprocess.check_call([pip, 'install', '-r', REQUIREMENTS])
    # Re-check after install
    installed = get_installed_packages()
    still_missing = [required[n] for n in required if n not in installed]
    if still_missing:
        print(f"{BOLD}{RED}ERROR: The following packages are still missing after install:{RESET} {', '.join(still_missing)}")
        print(f"{RED}If you are using extras (e.g., passlib[bcrypt]), ensure your pip version is up to date and try again.{RESET}")
        sys.exit(1)
    print(f"{BOLD}{GREEN}All required packages installed.{RESET}")

def main():
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
        # ANSI escape codes for bold and color
        BOLD = '\033[1m'
        YELLOW = '\033[93m'
        RESET = '\033[0m'
        print(f"\n{BOLD}{YELLOW}IMPORTANT: To activate your new environment, run:{RESET}")
        print(f"{BOLD}{YELLOW}  source .venv/bin/activate  {RESET}")
        print(f"{BOLD}After activation, use '.venv/bin/python' or 'python' (if shell is activated) to run project scripts.{RESET}")

if __name__ == '__main__':
    main()
