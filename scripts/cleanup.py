import sys
import argparse
import os
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

# Debug flag: set via env or CLI
DEBUG = os.environ.get('SMARTAI_DEBUG', '0') == '1'
def debug(msg):
    if DEBUG:
        print(f'[DEBUG] {msg}')
VENV_PATH = os.environ.get('SMARTAI_VENV_PATH', os.path.join(os.getcwd(), '.venv'))


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
        debug(f"Uninstalling all packages in .venv...")
        try:
            debug(f"Running: {pip} uninstall -y {' '.join(pkgs)}")
            subprocess.check_call([pip, 'uninstall', '-y'] + pkgs)
            debug(f"All packages uninstalled.")
        except Exception as e:
            debug(f"Error uninstalling packages: {e}")
            raise
    else:
        print(f"{BOLD}{GREEN}No packages to uninstall.{RESET}")

def remove_venv():
    GREEN = '\033[92m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    if os.environ.get("SMARTAI_TEST_MODE") == "1":
        print(f"{BOLD}{RED}Refusing to remove main .venv in test mode. Set SMARTAI_TEST_MODE=0 to allow removal.{RESET}")
        return
    if os.path.isdir(VENV_PATH):
        debug(f"Removing .venv directory...")
        try:
            debug(f"Running: shutil.rmtree({VENV_PATH})")
            shutil.rmtree(VENV_PATH)
            debug(f".venv removed.")
        except Exception as e:
            debug(f"Error removing .venv: {e}")
            raise
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

def interactive_cli():
    print("SmartAIPlatForm cleanup.py interactive mode. Type 'help' for options, 'exit' to quit.")
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    was_active = False
    while True:
        try:
            cmd = input("cleanup> ").strip().lower()
        except EOFError:
            print("\nInput error (EOF). Printing help and exiting.")
            print("Commands: help, exit, cleanup, info, version, reset, diagnostics")
            print("Exiting interactive mode.")
            break
        try:
            if cmd in ("exit", "quit"):
                print("Exiting interactive mode.")
                break
            elif cmd == "help":
                print("Commands: help, exit, cleanup, info, version, reset, diagnostics")
            elif cmd == "cleanup":
                try:
                    was_active = is_project_venv_active()
                except Exception:
                    was_active = False
                warn_if_active()
                uninstall_all_packages()
                remove_venv()
                GREEN = '\033[92m'
                BOLD = '\033[1m'
                RESET = '\033[0m'
                print(f"{BOLD}{GREEN}Cleanup complete.{RESET}")
                if was_active:
                    BOLD = '\033[1m'
                    YELLOW = '\033[93m'
                    RESET = '\033[0m'
                    print(f"\n{BOLD}{YELLOW}IMPORTANT: Your project virtual environment was active and has now been removed.{RESET}")
                    print(f"{BOLD}{YELLOW}Please run 'deactivate' in your shell to reset your prompt and environment.{RESET}")
            elif cmd == "info":
                print(f".venv path: {VENV_PATH}")
                print(f"Active environment: {os.environ.get('VIRTUAL_ENV')}")
                try:
                    pip = os.path.join(VENV_PATH, 'bin', 'pip')
                    out = subprocess.check_output([pip, 'freeze'], encoding='utf-8')
                    print(f"Installed packages:\n{out}")
                except Exception:
                    print("Could not list installed packages.")
            elif cmd == "version":
                print(f"cleanup.py version: 1.0.0")
                print(f"Python version: {sys.version}")
            elif cmd == "reset":
                if os.path.isdir(VENV_PATH):
                    debug("Removing existing .venv...")
                    try:
                        debug(f"Running: shutil.rmtree({VENV_PATH})")
                        shutil.rmtree(VENV_PATH)
                        debug(".venv removed.")
                    except Exception as e:
                        debug(f"Error removing .venv: {e}")
                        raise
                debug("Recreating .venv...")
                try:
                    debug(f"Running: {sys.executable} -m venv {VENV_PATH}")
                    subprocess.check_call([sys.executable, '-m', 'venv', VENV_PATH])
                    debug(".venv reset complete.")
                except Exception as e:
                    debug(f"Error recreating .venv: {e}")
                    raise
            elif cmd == "diagnostics":
                print("Running diagnostics...")
                print(f".venv path: {VENV_PATH}")
                print(f"Active environment: {os.environ.get('VIRTUAL_ENV')}")
                if not os.path.isdir(VENV_PATH):
                    print(".venv does not exist.")
                try:
                    pip = os.path.join(VENV_PATH, 'bin', 'pip')
                    out = subprocess.check_output([pip, 'freeze'], encoding='utf-8')
                    print(f"Installed packages:\n{out}")
                except Exception:
                    print("Could not list installed packages.")
                if os.path.exists(pip):
                    print("pip found in .venv.")
                else:
                    print("No pip found in .venv.")
            else:
                print("Unknown command. Type 'help'.")
        except Exception as exc:
            print(f"Error: {exc}")
        import sys
        sys.stdout.flush()
    print(f"{BOLD}{GREEN}Cleanup complete.{RESET}")
    if was_active:
        BOLD = '\033[1m'
        YELLOW = '\033[93m'
        RESET = '\033[0m'
        print(f"\n{BOLD}{YELLOW}IMPORTANT: Your project virtual environment was active and has now been removed.{RESET}")
        print(f"{BOLD}{YELLOW}Please run 'deactivate' in your shell to reset your prompt and environment.{RESET}")

def main():
    parser = argparse.ArgumentParser(description="SmartAIPlatForm cleanup.py")
    parser.add_argument("command", nargs="?", choices=["cleanup", "info", "version", "reset", "diagnostics"], help="Action to perform")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    global DEBUG
    DEBUG = args.debug or os.environ.get('SMARTAI_DEBUG', '0') == '1'
    if args.command is None:
        interactive_cli()
        return
    debug('Debug mode enabled via CLI argument.')
    if args.command == "cleanup":
        was_active = False
        try:
            was_active = is_project_venv_active()
        except Exception:
            was_active = False
        warn_if_active()
        uninstall_all_packages()
        remove_venv()
        GREEN = '\033[92m'
        BOLD = '\033[1m'
        RESET = '\033[0m'
        print(f"{BOLD}{GREEN}Cleanup complete.{RESET}")
        if was_active:
            BOLD = '\033[1m'
            YELLOW = '\033[93m'
            RESET = '\033[0m'
            print(f"\n{BOLD}{YELLOW}IMPORTANT: Your project virtual environment was active and has now been removed.{RESET}")
            print(f"{BOLD}{YELLOW}Please run 'deactivate' in your shell to reset your prompt and environment.{RESET}")
    elif args.command in ["info", "version", "reset", "diagnostics"]:
        print(f"Command '{args.command}' not yet implemented in main(). Use interactive mode.")
    else:
        print("Usage: cleanup.py [cleanup|info|version|reset|diagnostics] [--debug]")
        sys.exit(0)

if __name__ == '__main__':
    main()
