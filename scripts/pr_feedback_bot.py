#!/usr/bin/env python3
"""
Automated PR Feedback Bot
- Posts inline comments on pull requests for rule violations
- Summarizes violations and suggests fixes with doc links
- Integrates with GitHub API (requires GITHUB_TOKEN)
Category: automation
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from pathlib import Path
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser

try:
    from github import Github
except ImportError:
    print("PyGithub required. Install with: pip install PyGithub")
    sys.exit(1)

LOGS_DIR = Path(__file__).parent.parent / "logs"
VIOLATION_LOG = LOGS_DIR / "rule_violations.jsonl"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_NAME = os.environ.get("GITHUB_REPOSITORY")  # e.g. 'owner/repo'
PR_NUMBER = os.environ.get("PR_NUMBER")

DOCS_BASE = "https://github.com/OWNER/REPO/blob/main/docs/python_script_coding_rules.md"


def load_violations():
    if not VIOLATION_LOG.exists():
        return []
    with open(VIOLATION_LOG) as f:
        return [json.loads(line) for line in f if line.strip()]

def main():
    parser = get_arg_parser()
    parser.add_argument('--pr', type=int, help='PR number (overrides env)')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    pr_number = args.pr if args.pr is not None else os.environ.get("PR_NUMBER")
    repo_name = args.repo if hasattr(args, 'repo') and args.repo is not None else os.environ.get("GITHUB_REPOSITORY")
    github_token = args.token if hasattr(args, 'token') and args.token is not None else os.environ.get("GITHUB_TOKEN")
    if not (github_token and repo_name and pr_number):
        logger.error("GITHUB_TOKEN, GITHUB_REPOSITORY, and PR_NUMBER must be set.")
        print("Missing environment variables. Please set GITHUB_TOKEN, GITHUB_REPOSITORY, and PR_NUMBER in your .env file or environment.")
        print("See docs/github_setup.md for details.")
        sys.exit(1)
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    pr = repo.get_pull(int(pr_number))
    violations = load_violations()
    if not violations:
        logger.info("No rule violations to report.")
        return
    # Group by file/line
    comments = {}
    for v in violations:
        key = (v['file'], v.get('line', 1))
        msg = f"Rule violation: **{v['rule']}**\n{v.get('message','')}\n"
        if v.get('auto_fix_suggestion'):
            msg += f"Suggested fix: `{v['auto_fix_suggestion']}`\n"
        msg += f"[See docs]({DOCS_BASE}#{v['rule']})"
        comments.setdefault(key, []).append(msg)
    # Post review comments
    for (file, line), msgs in comments.items():
        body = '\n---\n'.join(msgs)
        try:
            pr.create_review_comment(body, pr.get_commits()[0].sha, file, line)
        except Exception as e:
            logger.error(f"Failed to comment on {file}:{line}: {e}")
    # Post summary
    summary = f"## Rule Violations ({len(violations)})\n"
    for v in violations:
        summary += f"- **{v['rule']}** in `{v['file']}`: {v.get('message','')}\n"
    pr.create_issue_comment(summary)
    logger.info("PR feedback posted.")

if __name__ == "__main__":
    main()
