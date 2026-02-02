import sys
#!/usr/bin/env python3
"""
cleanup.py: Cleans up the Python environment for SmartAIPlatForm.
- Uninstalls all packages in .venv
- Removes the .venv directory
- (Deactivation is handled by shell, but script will warn if .venv is active)
"""
import os
import shutil
import subprocess

VENV_PATH = os.path.join(os.getcwd(), '.venv')


def uninstall_all_packages():
    pip = os.path.join(VENV_PATH, 'bin', 'pip')
    GREEN = '\033[92m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    if not os.path.exists(pip):
        print(f"{BOLD}{RED}No .venv or pip found, skipping package uninstall.{RESET}")
        return
    out = subprocess.check_output([pip, 'freeze'], encoding='utf-8')
    pkgs = []
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Only uninstall lines that look like package==version or package
        if '==' in line:
            pkg = line.split('==')[0]
        elif '[' in line and ']' in line and '==' in line:
            pkg = line.split('[')[0]
        elif line.startswith('-e') or ' @ ' in line:
            # Skip editable installs and direct URLs
            continue
        else:
            pkg = line
        pkg = pkg.strip()
        if pkg:
            pkgs.append(pkg)
    if pkgs:
        print(f"{BOLD}Uninstalling all packages in .venv...{RESET}")
        subprocess.check_call([pip, 'uninstall', '-y'] + pkgs)
        print(f"{BOLD}{GREEN}All packages uninstalled.{RESET}")
    else:
        print(f"{BOLD}{GREEN}No packages to uninstall.{RESET}")

def remove_venv():
    GREEN = '\033[92m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    if os.path.isdir(VENV_PATH):
        print(f"{BOLD}Removing .venv directory...{RESET}")
        shutil.rmtree(VENV_PATH)
        print(f"{BOLD}{GREEN}.venv removed.{RESET}")
    else:
        print(f"{BOLD}{GREEN}No .venv directory to remove.{RESET}")


def is_project_venv_active():
    """
    Returns True if the currently active virtual environment matches this project's .venv.
    """
    active_venv = os.environ.get('VIRTUAL_ENV')
    if not active_venv:
        return False
    active_venv_path = os.path.normpath(os.path.realpath(active_venv))
    project_venv_path = os.path.normpath(os.path.realpath(VENV_PATH))
    return active_venv_path == project_venv_path

def warn_if_active():
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    if is_project_venv_active():
        print(f"{BOLD}{YELLOW}WARNING: .venv is currently active in this shell.{RESET}")
        print(f"{BOLD}{YELLOW}You should run 'deactivate' in your shell now, since the environment has been removed.{RESET}")

def main():
    was_active = is_project_venv_active()
    warn_if_active()
    uninstall_all_packages()
    remove_venv()
    GREEN = '\033[92m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    print(f"{BOLD}{GREEN}Cleanup complete.{RESET}")
    if was_active:
        # ANSI escape codes for bold and yellow
        BOLD = '\033[1m'
        YELLOW = '\033[93m'
        RESET = '\033[0m'
        print(f"\n{BOLD}{YELLOW}IMPORTANT: Your project virtual environment was active and has now been removed.{RESET}")
        print(f"{BOLD}{YELLOW}Please run 'deactivate' in your shell to reset your prompt and environment.{RESET}")

if __name__ == '__main__':
    main()
