#!/usr/bin/env python3

import csv
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import requests
import json
from pathlib import Path
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
"""
Script to sync SmartAIPlatform_Board.tsv with GitHub Issues.
- Creates issues for new board items not already present as issues.
- Requires a GitHub personal access token (with repo scope) in the GITHUB_TOKEN environment variable.
- Usage: python sync_board_to_github.py --repo patenile/SmartAIPlatForm --tsv docs/SmartAIPlatform_Board.tsv
Category: board
"""


GITHUB_API = "https://api.github.com"

def print_rule_and_fix(logger):
    mapping_path = Path(__file__).parent / "rule_mapping.json"
    if mapping_path.exists():
        with open(mapping_path) as f:
            rules = json.load(f)
        rule = rules.get("sync_board_to_github", {
            "rule": "Board TSV and GitHub issues must be kept in sync. Issues must be created for all board items.",
            "doc": "docs/SmartAIPlatform_Board.tsv",
            "fix": "Ensure GITHUB_TOKEN is set, repo is correct, and TSV is formatted properly. Fix any API errors and rerun the script."
        })
        logger.info(f"Rule: {rule.get('rule','')}")
        logger.info(f"See: {rule.get('doc','')}")
        logger.info(f"Suggested fix: {rule.get('fix','')}")

def get_existing_issues(repo, token, logger):
    issues = set()
    page = 1
    while True:
        url = f"{GITHUB_API}/repos/{repo}/issues?page={page}&state=all&per_page=100"
        resp = requests.get(url, headers={"Authorization": f"token {token}"})
        if resp.status_code != 200:
            logger.error(f"Failed to fetch issues: {resp.text}")
            print_rule_and_fix(logger)
            sys.exit(1)
        data = resp.json()
        if not data:
            break
        for issue in data:
            issues.add(issue["title"].strip())
        page += 1
    return issues

def create_issue(repo, token, title, logger, body=None, assignees=None):
    url = f"{GITHUB_API}/repos/{repo}/issues"
    payload = {"title": title}
    if body:
        payload["body"] = body
    if assignees:
        payload["assignees"] = assignees
    resp = requests.post(url, json=payload, headers={"Authorization": f"token {token}"})
    if resp.status_code not in (200, 201):
        logger.error(f"Failed to create issue '{title}': {resp.text}")
        print_rule_and_fix(logger)
    else:
        logger.info(f"Created issue: {title}")

def main():
    parser = get_arg_parser()
    parser.add_argument("--repo", required=True, help="GitHub repo, e.g. patenile/SmartAIPlatForm")
    parser.add_argument("--tsv", required=True, help="Path to TSV board file")
    args = parser.parse_args()
    if not args.repo or not args.tsv:
        print("Error: --repo and --tsv arguments are required. Example usage: python sync_board_to_github.py --repo owner/repo --tsv docs/SmartAIPlatform_Board.tsv")
        sys.exit(1)
    logger = get_logger(debug=args.debug)
    try:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            logger.error("Set GITHUB_TOKEN environment variable with a GitHub personal access token.")
            print_rule_and_fix(logger)
            sys.exit(1)
        existing = get_existing_issues(args.repo, token, logger)
        with open(args.tsv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                title = row["Title"].strip()
                url = row.get("URL", "").strip()
                assignees = [a.strip() for a in row.get("Assignees", "").split(',') if a.strip()]
                if title and title not in existing:
                    body = f"Imported from board TSV.\n\n{url}" if url else "Imported from board TSV."
                    create_issue(args.repo, token, title, logger, body, assignees if assignees else None)
                else:
                    logger.info(f"Issue already exists: {title}")
    except Exception as e:
        logger.error(f"Exception in sync_board_to_github: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
