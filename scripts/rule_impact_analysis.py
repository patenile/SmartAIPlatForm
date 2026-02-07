#!/usr/bin/env python3
"""
Automated Rule Impact Analysis
- Analyzes the impact of rule changes (add, remove, modify) on the codebase
- Reports which files, folders, or teams are affected by each rule change
- Can be run after rule_mapping.json or .smartai_rules.yaml changes
Category: automation
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from pathlib import Path
import os
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
from scripts.rule_config import load_rule_config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"
RULE_CONFIG_PATH = Path(__file__).parent.parent / ".smartai_rules.yaml"


def load_rule_mapping():
    if RULE_MAPPING_PATH.exists():
        with open(RULE_MAPPING_PATH) as f:
            return json.load(f)
    return {}

def get_py_files(root):
    return sorted([f for f in root.glob('**/*.py') if 'plugins/' not in str(f)])

def main():
    parser = get_arg_parser()
    parser.add_argument('--rule', type=str, help='Analyze impact for a specific rule (optional)')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    config = load_rule_config()
    mapping = load_rule_mapping()
    root = Path(__file__).parent.parent
    py_files = get_py_files(root)
    # Determine which rules are active for each file
    file_rule_map = {}
    for py_file in py_files:
        rel = str(py_file.relative_to(root))
        file_rule_map[rel] = []
        for rule in mapping:
            suppressed = config.get('suppressed_rules', {}).get(rule)
            if suppressed:
                continue
            skip = rule in (config.get('overrides', {}).get('skip_rules', []))
            if skip:
                continue
            file_rule_map[rel].append(rule)
    # Analyze impact
    if args.rule:
        rule = args.rule
        affected = [f for f, rules in file_rule_map.items() if rule in rules]
        logger.info(f"Rule '{rule}' affects {len(affected)} files:")
        for f in affected:
            logger.info(f"  {f}")
    else:
        logger.info("Rule impact analysis:")
        for rule in mapping:
            affected = [f for f, rules in file_rule_map.items() if rule in rules]
            logger.info(f"- {rule}: {len(affected)} files affected")
    # (Optional) Team mapping: if you have file/team mapping, add here
    # Example: team_map = {'scripts/': 'Automation', 'tests/': 'QA'}
    # ...

if __name__ == "__main__":
    main()
