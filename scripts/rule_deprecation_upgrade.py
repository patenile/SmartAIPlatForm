#!/usr/bin/env python3
"""
Rule Deprecation/Upgrade Automation
- Detects deprecated rules in rule_mapping.json
- Notifies users of deprecated rules in use
- Suggests or applies upgrades to new rules if available
- Can auto-update .smartai_rules.yaml and rule_mapping.json
Category: automation
"""
import sys
import json
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.central_logger import get_logger
import os
from scripts.central_args import get_arg_parser
from scripts.rule_config import load_rule_config, save_rule_config
from scripts.notify_slack import send_slack_notification
from scripts.notify_email import send_email_notification
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
    parser.add_argument('--slack', action='store_true', help='Notify via Slack')
    parser.add_argument('--email', action='store_true', help='Notify via email')
    parser.add_argument('--auto-upgrade', action='store_true', help='Auto-upgrade deprecated rules if possible')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    config = load_rule_config()
    mapping = load_rule_mapping()
    deprecated = {k: v for k, v in mapping.items() if v.get('deprecated')}
    if not deprecated:
        logger.info("No deprecated rules found.")
        return
    # Find deprecated rules in use
    in_use = []
    for rule in deprecated:
        if rule in (config.get('suppressed_rules') or {}):
            in_use.append(rule)
        if rule in (config.get('overrides') or {}):
            in_use.append(rule)
    if not in_use:
        logger.info("No deprecated rules in use.")
        return
    msg = ["Deprecated rules in use detected:"]
    for rule in in_use:
        info = deprecated[rule]
        msg.append(f"- {rule}: {info.get('deprecation_message', 'No message')}")
        if info.get('upgrade_to'):
            msg.append(f"  Suggested upgrade: {info['upgrade_to']}")
    # Auto-upgrade if requested
    upgraded = []
    if args.auto_upgrade:
        for rule in in_use:
            info = deprecated[rule]
            new_rule = info.get('upgrade_to')
            if new_rule:
                # Move config from old rule to new rule
                if 'suppressed_rules' in config and rule in config['suppressed_rules']:
                    config['suppressed_rules'][new_rule] = config['suppressed_rules'].pop(rule)
                if 'overrides' in config and rule in config['overrides']:
                    config['overrides'][new_rule] = config['overrides'].pop(rule)
                upgraded.append((rule, new_rule))
        if upgraded:
            save_rule_config(config)
            msg.append("\nAuto-upgraded rules:")
            for old, new in upgraded:
                msg.append(f"- {old} -> {new}")
    full_msg = "\n".join(msg)
    logger.info(full_msg)
    if args.slack:
        send_slack_notification(full_msg)
    if args.email:
        send_email_notification(subject="Rule Deprecation/Upgrade Notice", body=full_msg)

if __name__ == "__main__":
    main()
