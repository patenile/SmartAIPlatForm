#!/usr/bin/env python3
"""
Interactive Rule Onboarding Wizard
- Guides users to add, configure, and enable rules for their project.
- Updates .smartai_rules.yaml and rule_mapping.json as needed.
Category: automation
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from pathlib import Path
import os
from scripts.rule_config import load_rule_config, save_rule_config
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser

RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"
RULE_CONFIG_PATH = Path(__file__).parent.parent / ".smartai_rules.yaml"


def load_rule_mapping():
    if RULE_MAPPING_PATH.exists():
        with open(RULE_MAPPING_PATH) as f:
            return json.load(f)
    return {}

def prompt(msg, default=None):
    if default is not None:
        msg = f"{msg} [{default}]"
    val = input(msg + ": ").strip()
    return val if val else default

def main():
    parser = get_arg_parser()
    parser.add_argument('--dry-run', action='store_true', help='Show changes but do not write files')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    config = load_rule_config()
    mapping = load_rule_mapping()
    logger.info("Welcome to the Rule Onboarding Wizard!\n")
    # List available rules
    rules = list(mapping.keys())
    logger.info("Available rules:")
    for i, rule in enumerate(rules, 1):
        logger.info(f"  {i}. {rule} - {mapping[rule].get('description', '')}")
    # Select rules to enable
    sel = prompt("Enter rule numbers to enable (comma-separated, or 'all')", default='all')
    if sel.lower() == 'all':
        selected = rules
    else:
        selected = [rules[int(i)-1] for i in sel.split(',') if i.strip().isdigit() and 0 < int(i) <= len(rules)]
    logger.info(f"Selected rules: {selected}")
    # Configure each rule
    for rule in selected:
        logger.info(f"\nConfiguring rule: {rule}")
        desc = mapping[rule].get('description', '')
        logger.info(f"Description: {desc}")
        # Suppress?
        suppress = prompt(f"Suppress this rule? (y/N)", default='N').lower() == 'y'
        if suppress:
            reason = prompt("Reason for suppression", default='onboarding')
            config.setdefault('suppressed_rules', {})[rule] = reason
            continue
        # Override settings?
        if 'default_settings' in mapping[rule]:
            override = prompt("Override default settings? (y/N)", default='N').lower() == 'y'
            if override:
                config.setdefault('overrides', {})[rule] = {}
                for k, v in mapping[rule]['default_settings'].items():
                    val = prompt(f"Set {k}", default=str(v))
                    config['overrides'][rule][k] = type(v)(val)
    # Save or dry-run
    if args.dry_run:
        logger.info("\nDry run: would update .smartai_rules.yaml with:")
        logger.info(json.dumps(config, indent=2))
    else:
        save_rule_config(config)
        logger.info("\nUpdated .smartai_rules.yaml with new rule settings.")
    logger.info("Onboarding complete!")

if __name__ == "__main__":
    main()
