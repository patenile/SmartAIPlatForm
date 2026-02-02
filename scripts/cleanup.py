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
import sys

VENV_PATH = os.path.join(os.getcwd(), '.venv')


def uninstall_all_packages():
    pip = os.path.join(VENV_PATH, 'bin', 'pip')
    if not os.path.exists(pip):
        print('No .venv or pip found, skipping package uninstall.')
        return
    out = subprocess.check_output([pip, 'freeze'], encoding='utf-8')
    pkgs = [line.strip() for line in out.splitlines() if line and not line.startswith('#')]
    if pkgs:
        print('Uninstalling all packages in .venv...')
        subprocess.check_call([pip, 'uninstall', '-y'] + pkgs)
        print('All packages uninstalled.')
    else:
        print('No packages to uninstall.')

def remove_venv():
    if os.path.isdir(VENV_PATH):
        print('Removing .venv directory...')
        shutil.rmtree(VENV_PATH)
        print('.venv removed.')
    else:
        print('No .venv directory to remove.')

def warn_if_active():
    if os.environ.get('VIRTUAL_ENV'):
        print('WARNING: .venv is currently active in this shell.')
        print('You should run "deactivate" in your shell now, since the environment has been removed.')

def main():
    was_active = bool(os.environ.get('VIRTUAL_ENV'))
    warn_if_active()
    uninstall_all_packages()
    remove_venv()
    print('Cleanup complete.')
    if was_active:
        print('\nIMPORTANT: Your virtual environment was active and has now been removed.')
        print('Please run "deactivate" in your shell to reset your prompt and environment.')

if __name__ == '__main__':
    main()
