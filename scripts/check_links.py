#!/usr/bin/env python3
"""
check_links.py: Checks all Markdown files in the docs/ folder for broken internal and external links.
- Reports any broken links, missing files, or unreachable URLs.
- Can be extended to auto-update or fix links if needed.
"""
import re
import sys
import os
import requests
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
MD_LINK_RE = re.compile(r'\[(.*?)\]\((.*?)\)')
def is_url(link):
    return link.startswith('http://') or link.startswith('https://')
def check_url(url):
    try:
        resp = requests.head(url, allow_redirects=True, timeout=5)
        return resp.status_code < 400
    except Exception:
        return False

def check_file_link(base, link):
    # Remove anchors
    file_path = link.split('#')[0]
    if not file_path:
        return True
    abs_path = os.path.normpath(os.path.join(base, file_path))
    return os.path.exists(abs_path)

def main():
    # Warn if not running inside .venv
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    venv = os.environ.get('VIRTUAL_ENV')
    if not venv or not venv.endswith('.venv'):
        print(f"{BOLD}{YELLOW}WARNING: Not running inside project .venv! Activate with 'source .venv/bin/activate'.{RESET}")
    errors = []
    for root, _, files in os.walk(DOCS_DIR):
        for fname in files:
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath, encoding='utf-8') as f:
                text = f.read()
            for match in MD_LINK_RE.finditer(text):
                label, link = match.groups()
                if link.startswith('mailto:') or link.startswith('tel:'):
                    continue
                if is_url(link):
                    if not check_url(link):
                        errors.append(f"BROKEN URL: {link} in {fname} [{label}]")
                elif link.startswith('#'):
                    continue  # anchor only
                else:
                    if not check_file_link(os.path.dirname(fpath), link):
                        errors.append(f"MISSING FILE: {link} in {fname} [{label}]")
    if errors:
        print(f"\n{BOLD}{RED}Broken links found:{RESET}")
        for err in errors:
            print(f"{RED}- {err}{RESET}")
        # Only exit if not running interactively
        if not (hasattr(sys, 'ps1') or (len(sys.argv) == 1)):
            exit(1)
    else:
        print(f"{BOLD}{GREEN}All links OK.{RESET}")

def interactive_cli():
    print("SmartAIPlatForm check_links.py interactive mode. Type 'help' for options, 'exit' to quit.")
    while True:
        try:
            cmd = input("check_links> ").strip().lower()
        except EOFError:
            print("\nInput error (EOF). Printing help and exiting.")
            print("Commands: help, exit, check, status")
            print("Exiting interactive mode.")
            break
        try:
            if cmd in ("exit", "quit"):
                print("Exiting interactive mode.")
                break
            elif cmd == "help":
                print("Commands: help, exit, check, status")
            elif cmd == "check":
                main()
            elif cmd == "status":
                print("Docs directory:", DOCS_DIR)
                print("Markdown files:")
                for root, _, files in os.walk(DOCS_DIR):
                    for fname in files:
                        if fname.endswith('.md'):
                            print("-", fname)
            elif cmd == "info":
                print(f"Docs directory: {DOCS_DIR}")
                md_files = [f for f in os.listdir(DOCS_DIR) if f.endswith('.md')]
                print(f"Markdown files: {len(md_files)}")
            elif cmd == "version":
                print("check_links.py version: 1.0.0")
                import platform
                print(f"Python version: {platform.python_version()}")
            elif cmd == "reset":
                print("No cached results to reset.")
            elif cmd == "diagnostics":
                print("Running diagnostics...")
                try:
                    errors = []
                    YELLOW = '\033[93m'
                    GREEN = '\033[92m'
                    RED = '\033[91m'
                    BOLD = '\033[1m'
                    RESET = '\033[0m'
                    for root, _, files in os.walk(DOCS_DIR):
                        for fname in files:
                            if fname.endswith('.md'):
                                fpath = os.path.join(root, fname)
                                with open(fpath, encoding='utf-8') as f:
                                    for line in f:
                                        for match in re.finditer(r'\[(.*?)\]\((.*?)\)', line):
                                            label, link = match.groups()
                                            if is_url(link):
                                                try:
                                                    if not check_url(link):
                                                        errors.append(f"BROKEN URL: {link} in {fname} [{label}]")
                                                except Exception as e:
                                                    errors.append(f"ERROR checking URL: {link} in {fname} [{label}] ({e})")
                                            elif link.startswith('#'):
                                                continue
                                            else:
                                                if not check_file_link(os.path.dirname(fpath), link):
                                                    errors.append(f"MISSING FILE: {link} in {fname} [{label}]")
                    if errors:
                        print(f"\n{BOLD}{RED}Broken links found:{RESET}")
                        for err in errors[:20]:
                            print(f"{RED}- {err}{RESET}")
                        if len(errors) > 20:
                            print(f"{RED}...and {len(errors)-20} more errors not shown{RESET}")
                    else:
                        print(f"{BOLD}{GREEN}All links OK.{RESET}")
                except Exception as e:
                    print(f"Diagnostics error: {e}")
                import sys
                sys.stdout.flush()
                print("Diagnostics complete.")
                sys.stdout.flush()
                print()  # Ensure prompt is on a new line
                print("check_links> ", end="", flush=True)
                continue
            else:
                print("Unknown command. Type 'help'.")
        except Exception as exc:
            print(f"Error: {exc}")
        import sys
        sys.stdout.flush()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        interactive_cli()
    else:
        valid_args = {"check", "status", "info", "version", "reset", "diagnostics"}
        if any(arg in ("--help", "-h") for arg in sys.argv[1:]):
            print("Usage: check_links.py [check|status|info|version|reset|diagnostics]")
            sys.exit(0)
        # Fast exit for unknown arguments
        if not any(arg in valid_args for arg in sys.argv[1:]):
            print("Unknown argument(s):", sys.argv[1:])
            print("Usage: check_links.py [check|status|info|version|reset|diagnostics]")
            sys.exit(2)
        main()
