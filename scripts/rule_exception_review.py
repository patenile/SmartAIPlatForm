#!/usr/bin/env python3
"""
Rule Exception Expiry/Review Automation
- Tracks temporary rule suppressions/overrides with expiry dates
- Notifies or creates issues when exceptions are due for review or expired
Category: automation
"""
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pathlib import Path
import os
from datetime import datetime, timedelta
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
from scripts.rule_config import load_rule_config, save_rule_config
from scripts.notify_slack import send_slack_notification
from scripts.notify_email import send_email_notification
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

RULE_CONFIG_PATH = Path(__file__).parent.parent / ".smartai_rules.yaml"


def parse_expiry(reason):
    # Accepts 'until:YYYY-MM-DD' in reason
    if reason and 'until:' in reason:
        try:
            date_str = reason.split('until:')[1].split()[0]
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception:
            return None
    return None

def main():
    parser = get_arg_parser()
    parser.add_argument('--slack', action='store_true', help='Notify via Slack')
    parser.add_argument('--email', action='store_true', help='Notify via email')
    parser.add_argument('--auto-remove', action='store_true', help='Auto-remove expired exceptions')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    config = load_rule_config()
    suppressed = config.get('suppressed_rules', {})
    today = datetime.now().date()
    due = []
    expired = []
    for rule, reason in suppressed.items():
        expiry = parse_expiry(str(reason))
        if expiry:
            if expiry < today:
                expired.append((rule, reason, expiry))
            elif expiry <= today + timedelta(days=7):
                due.append((rule, reason, expiry))
    msg = []
    if due:
        msg.append("Rule exceptions due for review soon:")
        for rule, reason, expiry in due:
            msg.append(f"- {rule}: {reason} (expires {expiry})")
    if expired:
        msg.append("Rule exceptions expired:")
        for rule, reason, expiry in expired:
            msg.append(f"- {rule}: {reason} (expired {expiry})")
    if not msg:
        logger.info("No rule exceptions due or expired.")
    else:
        full_msg = "\n".join(msg)
        logger.info(full_msg)
        if args.slack:
            send_slack_notification(full_msg)
        if args.email:
            send_email_notification(subject="Rule Exception Review", body=full_msg)
    # Auto-remove expired
    if args.auto_remove and expired:
        for rule, _, _ in expired:
            suppressed.pop(rule, None)
        config['suppressed_rules'] = suppressed
        save_rule_config(config)
        logger.info("Expired exceptions removed from config.")

if __name__ == "__main__":
    main()
