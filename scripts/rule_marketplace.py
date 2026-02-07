#!/usr/bin/env python3
"""
Rule Marketplace/Registry Integration
- Discover, import, and share rules from a central registry (local or remote)
- Supports listing, searching, importing, and publishing rules
Category: automation
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
import shutil
from pathlib import Path
import os
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# For demo: use a local directory as the registry
REGISTRY_PATH = Path(__file__).parent.parent / "rule_registry"
RULES_DIR = Path(__file__).parent
RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"


def ensure_registry():
    REGISTRY_PATH.mkdir(exist_ok=True)

def list_registry():
    ensure_registry()
    return [f for f in REGISTRY_PATH.glob('check_*.py')]

def import_rule(rule_name):
    ensure_registry()
    src = REGISTRY_PATH / rule_name
    dest = RULES_DIR / rule_name
    if not src.exists():
        return False, f"Rule {rule_name} not found in registry."
    shutil.copy(src, dest)
    return True, f"Imported {rule_name} to scripts/."

def publish_rule(rule_name):
    src = RULES_DIR / rule_name
    dest = REGISTRY_PATH / rule_name
    if not src.exists():
        return False, f"Rule {rule_name} not found in scripts/."
    shutil.copy(src, dest)
    return True, f"Published {rule_name} to registry."

def main():
    parser = get_arg_parser()
    parser.add_argument('--list', action='store_true', help='List rules in registry')
    parser.add_argument('--import-rule', type=str, help='Import rule from registry')
    parser.add_argument('--publish-rule', type=str, help='Publish rule to registry')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    if args.list:
        rules = list_registry()
        if not rules:
            logger.info("No rules found in registry.")
        else:
            logger.info("Rules in registry:")
            for r in rules:
                logger.info(f"- {r.name}")
    elif args.import_rule:
        ok, msg = import_rule(args.import_rule)
        logger.info(msg)
    elif args.publish_rule:
        ok, msg = publish_rule(args.publish_rule)
        logger.info(msg)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
