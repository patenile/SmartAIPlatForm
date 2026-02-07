#!/usr/bin/env python3
"""
Rule Severity Levels & Enforcement Modes
- Supports severity: error, warning, info
- Supports enforcement: block, warn, log-only
- Updates rule_mapping.json and .smartai_rules.yaml to include severity and enforcement
- Provides a CLI to set or update these for each rule
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"
RULE_CONFIG_PATH = Path(__file__).parent.parent / ".smartai_rules.yaml"

SEVERITIES = ["error", "warning", "info"]
ENFORCEMENTS = ["block", "warn", "log-only"]


def load_rule_mapping():
    if RULE_MAPPING_PATH.exists():
        with open(RULE_MAPPING_PATH) as f:
            return json.load(f)
    return {}

def save_rule_mapping(mapping):
    with open(RULE_MAPPING_PATH, "w") as f:
        json.dump(mapping, f, indent=2)

def main():
    parser = get_arg_parser()
    parser.add_argument('--set', nargs=3, metavar=('RULE', 'SEVERITY', 'ENFORCEMENT'), help='Set severity and enforcement for a rule')
    parser.add_argument('--list', action='store_true', help='List all rules with severity and enforcement')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    mapping = load_rule_mapping()
    if args.set:
        rule, severity, enforcement = args.set
        if rule not in mapping:
            logger.error(f"Rule '{rule}' not found in rule_mapping.json")
            sys.exit(1)
        if severity not in SEVERITIES:
            logger.error(f"Invalid severity: {severity}")
            sys.exit(1)
        if enforcement not in ENFORCEMENTS:
            logger.error(f"Invalid enforcement: {enforcement}")
            sys.exit(1)
        mapping[rule]['severity'] = severity
        mapping[rule]['enforcement'] = enforcement
        save_rule_mapping(mapping)
        logger.info(f"Updated {rule}: severity={severity}, enforcement={enforcement}")
    elif args.list:
        logger.info("Rule | Severity | Enforcement")
        logger.info("-----|----------|------------")
        for rule, meta in mapping.items():
            logger.info(f"{rule} | {meta.get('severity','error')} | {meta.get('enforcement','block')}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
