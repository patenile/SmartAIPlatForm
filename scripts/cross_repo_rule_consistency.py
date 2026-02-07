#!/usr/bin/env python3
"""
Cross-Repo Rule Consistency Checker
- Compares rule_mapping.json and .smartai_rules.yaml across multiple repos
- Reports inconsistencies and suggests sync actions
Category: automation
"""
import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pathlib import Path

from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser

def load_json(path):
    if not Path(path).exists():
        return None
    with open(path) as f:
        return json.load(f)

def load_yaml_lines(path):
    if not Path(path).exists():
        return None
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]

def compare_dicts(d1, d2):
    keys1 = set(d1 or {})
    keys2 = set(d2 or {})
    added = keys2 - keys1
    removed = keys1 - keys2
    changed = {k for k in (keys1 & keys2) if d1[k] != d2[k]}
    return added, removed, changed

def main():
    parser = get_arg_parser()
    parser.add_argument('--repos', nargs='+', required=True, help='Paths to other repos to check')
    args = parser.parse_args()
    if not args.repos:
        print("Error: --repos argument is required. Example usage: python cross_repo_rule_consistency.py --repos repo1 repo2")
        sys.exit(1)
    logger = get_logger(debug=args.debug)
    this_root = Path(__file__).parent.parent
    this_mapping = load_json(this_root / 'rule_mapping.json')
    this_config = load_yaml_lines(this_root / '.smartai_rules.yaml')
    for repo in args.repos:
        repo_path = Path(repo)
        logger.info(f"\nChecking repo: {repo_path}")
        mapping = load_json(repo_path / 'rule_mapping.json')
        config = load_yaml_lines(repo_path / '.smartai_rules.yaml')
        if mapping is None or config is None:
            logger.warning(f"Missing rule_mapping.json or .smartai_rules.yaml in {repo}")
            continue
        # Compare mapping
        a, r, c = compare_dicts(this_mapping, mapping)
        if a or r or c:
            logger.info("rule_mapping.json differences:")
            if a:
                logger.info(f"  Added: {a}")
            if r:
                logger.info(f"  Removed: {r}")
            if c:
                logger.info(f"  Changed: {c}")
        else:
            logger.info("rule_mapping.json is consistent.")
        # Compare config (line-based)
        if this_config != config:
            logger.info(".smartai_rules.yaml differs.")
        else:
            logger.info(".smartai_rules.yaml is consistent.")

if __name__ == "__main__":
    main()
