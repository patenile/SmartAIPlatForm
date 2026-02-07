#!/usr/bin/env python3
"""
Rule Adoption Analytics
- Tracks which rules are most/least adopted across teams or projects
- Recommends deprecation or promotion based on usage
Category: automation
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from pathlib import Path
from collections import Counter
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser

RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"
FILE_OWNERSHIP_PATH = Path(__file__).parent.parent / "file_ownership.json"
VIOLATION_LOG = Path(__file__).parent.parent / "logs/rule_violations.jsonl"


def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def load_violations():
    if not VIOLATION_LOG.exists():
        return []
    with open(VIOLATION_LOG) as f:
        return [json.loads(line) for line in f if line.strip()]

def main():
    parser = get_arg_parser()
    parser.add_argument('--report', action='store_true', help='Show rule adoption analytics')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    mapping = load_json(RULE_MAPPING_PATH)
    file_owners = load_json(FILE_OWNERSHIP_PATH)
    violations = load_violations()
    # Count rule usage (by violation and by config presence)
    rule_counts = Counter(v['rule'] for v in violations)
    owner_counts = Counter(file_owners.values())
    logger.info("Rule Adoption Analytics Report:")
    logger.info("Rule | Violations | Owner(s)")
    logger.info("-----|-----------|---------")
    for rule in mapping:
        owners = set()
        for file, owner in file_owners.items():
            if rule in (mapping.get(rule, {}).get('applies_to', []) or []) or rule in (mapping.get(rule, {}).get('script', '')):
                owners.add(owner)
        logger.info(f"{rule} | {rule_counts.get(rule,0)} | {', '.join(owners) if owners else '-'}")
    # Recommend deprecation/promotion
    least_used = [r for r, c in rule_counts.items() if c == min(rule_counts.values())]
    most_used = [r for r, c in rule_counts.items() if c == max(rule_counts.values())]
    logger.info(f"\nRecommend deprecation: {', '.join(least_used)}")
    logger.info(f"Recommend promotion: {', '.join(most_used)}")

if __name__ == "__main__":
    main()
