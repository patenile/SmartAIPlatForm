#!/usr/bin/env python3
"""
Auto-create GitHub issues for critical security findings from safety or pip-audit reports.
Category: security
"""
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
import sys
import requests
import re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser

def create_github_issue(repo, token, title, body, logger):
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {"Authorization": f"token {token}"}
    payload = {"title": title, "body": body}
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code not in (200, 201):
        logger.error(f"Failed to create issue: {resp.text}")
    else:
        logger.info(f"Created GitHub issue: {title}")

def main():
    parser = get_arg_parser()
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    try:
        repo = os.environ.get("GITHUB_REPOSITORY")
        token = os.environ.get("GITHUB_TOKEN")
        if not repo or not token:
            logger.error("GITHUB_REPOSITORY and GITHUB_TOKEN must be set in the environment.")
            sys.exit(1)
        # Read safety or pip-audit report from stdin
        report = sys.stdin.read()
        criticals = re.findall(r'CRITICAL.*?\n.*?\n', report, re.DOTALL)
        for finding in criticals:
            title = finding.split('\n')[0][:80]
            body = finding
            create_github_issue(repo, token, title, body, logger)
        if not criticals:
            logger.info("No critical security findings to report.")
    except Exception as e:
        logger.error(f"Exception in auto_create_security_issues: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
