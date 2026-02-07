#!/usr/bin/env python3
"""
Rule-Aware Code Review Assignment
- Assigns PR reviewers based on rule ownership or recent violations in changed files
- Integrates with file_ownership.json and rule_mapping.json
Category: automation
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from pathlib import Path
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

FILE_OWNERSHIP_PATH = Path(__file__).parent.parent / "file_ownership.json"
RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"


def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def get_changed_files():
    # Use git to get changed files in the PR (or last commit)
    import subprocess
    try:
        files = subprocess.check_output(["git", "diff", "--name-only", "origin/main...HEAD"]).decode().splitlines()
        return [f for f in files if f.endswith('.py')]
    except Exception:
        return []

def main():
    parser = get_arg_parser()
    parser.add_argument('--assign', action='store_true', help='Suggest reviewers for changed files')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    file_owners = load_json(FILE_OWNERSHIP_PATH)
    rule_mapping = load_json(RULE_MAPPING_PATH)
    if args.assign:
        changed = get_changed_files()
        reviewers = set()
        for f in changed:
            owner = file_owners.get(f)
            if owner:
                reviewers.add(owner)
            # Also add rule owners for rules that apply to this file
            for rule, meta in rule_mapping.items():
                if meta.get('owner'):
                    # Simple heuristic: if rule script name in file name
                    if rule in f:
                        reviewers.add(meta['owner'])
        if reviewers:
            logger.info(f"Suggested reviewers: {', '.join(reviewers)}")
        else:
            logger.info("No reviewers found for changed files.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
