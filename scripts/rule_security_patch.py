#!/usr/bin/env python3
"""
Automated Security Patch for Rule Scripts
- Scans rule scripts for vulnerabilities (e.g., insecure imports, eval, subprocess)
- Auto-patches or notifies maintainers if issues are found
Category: automation
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import ast
import os
from pathlib import Path
import json
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
from scripts.notify_slack import send_slack_notification
from scripts.notify_email import send_email_notification
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

RULES_DIR = Path(__file__).parent

DANGEROUS = ["eval", "exec", "os.system", "subprocess", "input"]


def scan_script(path):
    with open(path) as f:
        tree = ast.parse(f.read(), filename=str(path))
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = getattr(node.func, 'id', None) or getattr(getattr(node.func, 'attr', None), 'id', None)
            if func and func in DANGEROUS:
                issues.append((func, node.lineno))
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in ("os", "subprocess"):
                    issues.append((f"import {alias.name}", node.lineno))
        if isinstance(node, ast.ImportFrom):
            if node.module in ("os", "subprocess"):
                issues.append((f"from {node.module} import ...", node.lineno))
    return issues

def main():
    parser = get_arg_parser()
    parser.add_argument('--scan', action='store_true', help='Scan all rule scripts for security issues')
    parser.add_argument('--patch', action='store_true', help='Auto-patch (comment out) dangerous lines')
    parser.add_argument('--notify', action='store_true', help='Notify maintainers if issues found')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    issues_found = False
    for script in RULES_DIR.glob('check_*.py'):
        issues = scan_script(script)
        if issues:
            issues_found = True
            logger.warning(f"Security issues in {script}:")
            for func, lineno in issues:
                logger.warning(f"  {func} at line {lineno}")
            if args.patch:
                # Comment out dangerous lines (simple, not perfect)
                lines = script.read_text().splitlines()
                for func, lineno in issues:
                    idx = lineno - 1
                    if not lines[idx].lstrip().startswith('#'):
                        lines[idx] = '# PATCHED: ' + lines[idx]
                script.write_text('\n'.join(lines))
                logger.info(f"Patched {script}")
    if issues_found and args.notify:
        msg = "Security issues found in rule scripts. See logs for details."
        send_slack_notification(msg)
        send_email_notification(subject="Rule Script Security Alert", body=msg)
    if not (args.scan or args.patch or args.notify):
        parser.print_help()

if __name__ == "__main__":
    main()
