#!/usr/bin/env python3
"""
setup_env.py: Ensures .venv exists, creates it with python3.12 if missing, and checks/installs required packages from requirements.txt.
"""
import os
import subprocess
import sys
import shutil

VENV_PATH = os.path.join(os.getcwd(), '.venv')
PYTHON_BIN = '/opt/homebrew/bin/python3.12'
REQUIREMENTS = 'requirements.txt'


def venv_exists():
    return os.path.isdir(VENV_PATH) and os.path.isfile(os.path.join(VENV_PATH, 'bin', 'activate'))

def create_venv():
    print('Creating .venv with python3.12...')
    subprocess.check_call([PYTHON_BIN, '-m', 'venv', '.venv'])
    print('Created .venv')


def get_installed_packages():
    pip = os.path.join(VENV_PATH, 'bin', 'pip')
    out = subprocess.check_output([pip, 'freeze'], encoding='utf-8')
    pkgs = set()
    for line in out.splitlines():
        if '==' in line:
            pkg = line.split('==')[0].lower()
            # Strip extras if present
            if '[' in pkg and ']' in pkg:
                pkg = pkg.split('[')[0]
            # Normalize: remove '-' and '_'
            pkg = pkg.replace('-', '').replace('_', '')
            pkgs.add(pkg)
        # Ignore lines without '==' (not a package)
    return pkgs


def get_required_packages():
    if not os.path.exists(REQUIREMENTS):
        print(f"ERROR: {REQUIREMENTS} not found.")
        sys.exit(1)
    with open(REQUIREMENTS) as f:
        pkgs = set()
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Handle extras: passlib[bcrypt]
            pkg = line.split('==')[0].split('>=')[0].split('<=')[0].lower()
            # Strip extras if present
            if '[' in pkg and ']' in pkg:
                pkg = pkg.split('[')[0]
            # Normalize: remove '-' and '_'
            pkg = pkg.replace('-', '').replace('_', '')
            pkgs.add(pkg)
        return pkgs


def install_missing_packages():
    pip = os.path.join(VENV_PATH, 'bin', 'pip')
    # Always upgrade pip first
    print('Upgrading pip...')
    subprocess.check_call([pip, 'install', '--upgrade', 'pip'])
    required = get_required_packages()
    installed = get_installed_packages()
    # Compare base package names only
    missing = required - installed
    if not missing:
        print('All required packages are already installed.')
        return
    print('Installing missing packages:', ', '.join(missing))
    subprocess.check_call([pip, 'install', '-r', REQUIREMENTS])
    # Re-check after install
    installed = get_installed_packages()
    still_missing = required - installed
    if still_missing:
        print('ERROR: The following packages are still missing after install:', ', '.join(still_missing))
        print('If you are using extras (e.g., passlib[bcrypt]), ensure your pip version is up to date and try again.')
        sys.exit(1)
    print('All required packages installed.')

def main():
    first_time = False
    if not venv_exists():
        create_venv()
        first_time = True
    else:
        print('.venv already exists.')
    install_missing_packages()
    print('Environment setup complete.')
    if first_time:
        print('\nTo activate your new environment, run:')
        print('  source .venv/bin/activate')
        print('After activation, use ".venv/bin/python" or "python" (if shell is activated) to run project scripts.')

if __name__ == '__main__':
    main()
