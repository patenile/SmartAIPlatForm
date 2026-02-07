#!/usr/bin/env python3
"""
Automated Rollback/Hotfix for Rule Failures
- Detects if a new rule or config breaks CI (via logs or status)
- Auto-reverts the last rule/config change and notifies maintainers
- Optionally creates a hotfix branch or issue
Category: automation
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
import subprocess
from pathlib import Path
import os
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
from scripts.notify_slack import send_slack_notification
from scripts.notify_email import send_email_notification
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"
RULE_CONFIG_PATH = Path(__file__).parent.parent / ".smartai_rules.yaml"


def git(cmd):
    return subprocess.check_output(["git"] + cmd, text=True).strip()

def get_last_rule_change():
    # Find last commit that touched rule_mapping.json or .smartai_rules.yaml
    log = git(["log", "--pretty=format:%H", f"--", str(RULE_MAPPING_PATH), str(RULE_CONFIG_PATH)])
    return log.splitlines()[0] if log else None

def revert_commit(commit):
    git(["revert", "--no-edit", commit])

def main():
    parser = get_arg_parser()
    parser.add_argument('--ci-log', type=str, help='Path to CI log file (optional)')
    parser.add_argument('--auto-revert', action='store_true', help='Auto-revert last rule/config change if failure detected')
    parser.add_argument('--notify', action='store_true', help='Notify maintainers on revert')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    # Detect failure (simple: look for 'FAIL' in CI log or nonzero exit)
    failed = False
    if args.ci_log:
        log_path = Path(args.ci_log)
        if log_path.exists() and 'FAIL' in log_path.read_text():
            failed = True
    else:
        # Assume run from CI failure context
        failed = True
    if not failed:
        logger.info("No rule/config failure detected.")
        return
    last_commit = get_last_rule_change()
    if not last_commit:
        logger.info("No recent rule/config change found.")
        return
    if args.auto_revert:
        revert_commit(last_commit)
        logger.info(f"Reverted commit {last_commit} due to rule/config failure.")
        msg = f"Automated rollback: commit {last_commit} reverted due to rule/config failure."
        if args.notify:
            send_slack_notification(msg)
            send_email_notification(subject="Rule Rollback Performed", body=msg)
    else:
        logger.info(f"Would revert commit {last_commit} (use --auto-revert to apply)")

if __name__ == "__main__":
    main()
