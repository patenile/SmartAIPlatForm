#!/usr/bin/env python3
"""
Rule 'What-If' Simulator
- Simulates the impact of enabling/disabling rules before applying changes
- Shows which files, checks, and teams would be affected
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
FILE_OWNERSHIP_PATH = Path(__file__).parent.parent / "file_ownership.json"


def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def get_py_files(root):
    return sorted([f for f in root.glob('**/*.py') if 'plugins/' not in str(f)])

def main():
    parser = get_arg_parser()
    parser.add_argument('--enable', nargs='+', help='Simulate enabling these rules')
    parser.add_argument('--disable', nargs='+', help='Simulate disabling these rules')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    mapping = load_json(RULE_MAPPING_PATH)
    config = load_rule_config()
    file_owners = load_json(FILE_OWNERSHIP_PATH)
    root = Path(__file__).parent.parent
    py_files = get_py_files(root)
    # Simulate config
    suppressed = set((config.get('suppressed_rules') or {}).keys())
    if args.enable:
        suppressed -= set(args.enable)
    if args.disable:
        suppressed |= set(args.disable)
    # Build impact matrix
    impact = {}
    for py_file in py_files:
        rel = str(py_file.relative_to(root))
        impact[rel] = []
        for rule in mapping:
            if rule not in suppressed:
                impact[rel].append(rule)
    # Report
    logger.info("What-If Simulation Result:")
    for rule in (args.enable or []) + (args.disable or []):
        affected = [f for f, rules in impact.items() if rule in rules]
        owners = set(file_owners.get(f, '-') for f in affected)
        logger.info(f"Rule '{rule}': {len(affected)} files affected, owners: {', '.join(owners)}")
        for f in affected:
            logger.info(f"  {f}")
    logger.info("Simulation complete. No changes applied.")

if __name__ == "__main__":
    main()
