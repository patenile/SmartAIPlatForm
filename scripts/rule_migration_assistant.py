#!/usr/bin/env python3
"""
Automated Rule Migration Assistant
- Suggests or auto-migrates rules when upgrading frameworks or dependencies
- Scans for deprecated rules and maps to new best practices
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
from scripts.rule_config import load_rule_config, save_rule_config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"
RULE_CONFIG_PATH = Path(__file__).parent.parent / ".smartai_rules.yaml"


def load_rule_mapping():
    if RULE_MAPPING_PATH.exists():
        with open(RULE_MAPPING_PATH) as f:
            return json.load(f)
    return {}

def main():
    parser = get_arg_parser()
    parser.add_argument('--suggest', action='store_true', help='Suggest rule migrations')
    parser.add_argument('--apply', action='store_true', help='Auto-migrate deprecated rules')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    config = load_rule_config()
    mapping = load_rule_mapping()
    deprecated = {k: v for k, v in mapping.items() if v.get('deprecated') and v.get('upgrade_to')}
    migrations = []
    for rule, meta in deprecated.items():
        if rule in (config.get('suppressed_rules') or {}) or rule in (config.get('overrides') or {}):
            migrations.append((rule, meta['upgrade_to']))
    if args.suggest:
        if not migrations:
            logger.info("No rule migrations needed.")
        else:
            logger.info("Rule migration suggestions:")
            for old, new in migrations:
                logger.info(f"- {old} -> {new}")
    if args.apply and migrations:
        for old, new in migrations:
            # Move config from old rule to new rule
            if 'suppressed_rules' in config and old in config['suppressed_rules']:
                config['suppressed_rules'][new] = config['suppressed_rules'].pop(old)
            if 'overrides' in config and old in config['overrides']:
                config['overrides'][new] = config['overrides'].pop(old)
        save_rule_config(config)
        logger.info("Rule migrations applied.")
    if not (args.suggest or args.apply):
        parser.print_help()

if __name__ == "__main__":
    main()
