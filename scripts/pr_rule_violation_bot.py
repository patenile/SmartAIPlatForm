#!/usr/bin/env python3
"""
Bot to comment on PRs with rule violations and suggestions (GitHub Actions usage).
Category: automation
"""


import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import requests
import json
import re
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser


def parse_violations(markdown):
    """
    Parse rule violation markdown table into a list of dicts.
    Expects a markdown table with columns: Script | Category | Status
    """
    lines = markdown.splitlines()
    table_lines = [l for l in lines if l.strip() and '|' in l]
    if not table_lines:
        return []
    # Find header and data lines
    header_idx = 0
    for i, l in enumerate(table_lines):
        if re.match(r'\|?\s*Script\s*\|', l):
            header_idx = i
            break
    data_lines = table_lines[header_idx+2:]  # skip header and separator
    violations = []
    for l in data_lines:
        parts = [p.strip() for p in l.strip('|').split('|')]
        if len(parts) >= 3 and parts[2].upper() == 'FAIL':
            violations.append({
                'script': parts[0],
                'category': parts[1],
                'status': parts[2]
            })
    return violations

def post_pr_comment(pr_url, token, body, logger):
    headers = {"Authorization": f"token {token}"}
    resp = requests.post(f"{pr_url}/comments", json={"body": body}, headers=headers)
    if resp.status_code not in (200, 201):
        logger.error(f"Failed to comment on PR: {resp.text}")
    else:
        logger.info("Commented on PR with rule violations.")

def post_check_run_annotations(token, check_run_id, repo, sha, violations, logger):
    """
    Post annotations to GitHub Checks API for each violation (summary only, not true inline).
    """
    url = f"https://api.github.com/repos/{repo}/check-runs/{check_run_id}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    summary = f"Rule violations detected: {len(violations)}\n" + '\n'.join(f"- {v['script']} [{v['category']}]" for v in violations)
    data = {
        "output": {
            "title": "Rule Violation Report",
            "summary": summary,
            "annotations": []  # Could be filled with file/line if available
        }
    }
    resp = requests.patch(url, headers=headers, data=json.dumps(data))
    if resp.status_code not in (200, 201):
        logger.error(f"Failed to update check run: {resp.text}")
    else:
        logger.info("Updated GitHub Check Run with summary.")

def main():
    parser = get_arg_parser()
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    try:
        pr_url = args.pr_url if hasattr(args, 'pr_url') and args.pr_url is not None else os.environ.get("GITHUB_PR_URL")
        token = args.token if hasattr(args, 'token') and args.token is not None else os.environ.get("GITHUB_TOKEN")
        check_run_id = args.check_run_id if hasattr(args, 'check_run_id') and args.check_run_id is not None else os.environ.get("GITHUB_CHECK_RUN_ID")
        repo = args.repo if hasattr(args, 'repo') and args.repo is not None else os.environ.get("GITHUB_REPOSITORY")
        sha = args.sha if hasattr(args, 'sha') and args.sha is not None else os.environ.get("GITHUB_SHA")
        if not pr_url or not token:
            logger.error("GITHUB_PR_URL and GITHUB_TOKEN must be set in the environment or passed as arguments.")
            print("Missing environment variables. Please set GITHUB_PR_URL and GITHUB_TOKEN in your .env file or environment.")
            print("See docs/github_setup.md for details.")
            sys.exit(1)
        comment = sys.stdin.read()
        violations = parse_violations(comment)
        # Post summary comment
        post_pr_comment(pr_url, token, comment, logger)
        # If running in a GitHub Check context, update check run with summary
        if check_run_id and repo and sha and violations:
            post_check_run_annotations(token, check_run_id, repo, sha, violations, logger)
    except Exception as e:
        logger.error(f"Exception in pr_rule_violation_bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
