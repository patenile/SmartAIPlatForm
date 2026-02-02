#!/usr/bin/env python3
#!/usr/bin/env python3
"""
check_links.py: Checks all Markdown files in the docs/ folder for broken internal and external links.
- Reports any broken links, missing files, or unreachable URLs.
- Can be extended to auto-update or fix links if needed.
"""
import os
import re
import requests
from urllib.parse import urlparse

DOCS_DIR = os.path.join(os.path.dirname(__file__), 'docs')
MD_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

def is_url(link):
    return bool(urlparse(link).scheme in ('http', 'https'))

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
        exit(1)
    else:
        print(f"{BOLD}{GREEN}All links OK.{RESET}")

if __name__ == '__main__':
    main()
