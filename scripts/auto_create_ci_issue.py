#!/usr/bin/env python3

import sys, os
import requests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
"""
Auto-create a GitHub issue for CI/CD failures (self-healing automation).
Category: automation
"""
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def main():
    parser = get_arg_parser()
    parser.add_argument('--title', required=True, help='Issue title')
    parser.add_argument('--body', required=True, help='Issue body')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    if not args.title or not args.body:
        logger = get_logger(debug=args.debug)
        logger.error("Error: --title and --body arguments are required. Example usage: python auto_create_ci_issue.py --title 'CI Failure' --body 'The CI pipeline failed due to XYZ reason.'")  
        sys.exit(1)
    try:
        repo = args.repo if hasattr(args, 'repo') and args.repo is not None else os.environ.get("GITHUB_REPOSITORY")
        token = args.token if hasattr(args, 'token') and args.token is not None else os.environ.get("GITHUB_TOKEN")
        if not repo or not token:
            logger.error("GITHUB_REPOSITORY and GITHUB_TOKEN must be set in the environment or passed as arguments.")
            sys.exit(1)
        url = f"https://api.github.com/repos/{repo}/issues"
        headers = {"Authorization": f"token {token}"}
        payload = {"title": args.title, "body": args.body}
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code not in (200, 201):
            logger.error(f"Failed to create CI failure issue: {resp.text}")
            sys.exit(1)
        logger.info("Created GitHub issue for CI/CD failure.")
    except Exception as e:
        logger.error(f"Exception in auto_create_ci_issue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
