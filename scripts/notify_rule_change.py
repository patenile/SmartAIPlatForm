#!/usr/bin/env python3
"""
Rule Change Notification Script
- Detects changes to rule_mapping.json or .smartai_rules.yaml
- Notifies via Slack and/or email if rules are added, removed, or modified
Category: automation
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
import difflib
from pathlib import Path
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
from scripts.notify_slack import send_slack_notification
from scripts.notify_email import send_email_notification

RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"
RULE_CONFIG_PATH = Path(__file__).parent.parent / ".smartai_rules.yaml"
SNAPSHOT_DIR = Path(__file__).parent.parent / ".rule_snapshots"


def load_file(path):
    if not path.exists():
        return None
    if path.suffix == ".json":
        with open(path) as f:
            return json.load(f)
    else:
        with open(path) as f:
            return f.read().splitlines()

def save_snapshot(name, data):
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    snap = SNAPSHOT_DIR / name
    if isinstance(data, dict):
        with open(snap, "w") as f:
            json.dump(data, f, indent=2)
    else:
        with open(snap, "w") as f:
            f.write("\n".join(data))

def load_snapshot(name):
    snap = SNAPSHOT_DIR / name
    if not snap.exists():
        return None
    if name.endswith(".json"):
        with open(snap) as f:
            return json.load(f)
    else:
        with open(snap) as f:
            return f.read().splitlines()

def diff_dicts(old, new):
    old_keys = set(old or {})
    new_keys = set(new or {})
    added = new_keys - old_keys
    removed = old_keys - new_keys
    changed = {k for k in (old_keys & new_keys) if old[k] != new[k]}
    return added, removed, changed

def main():
    parser = get_arg_parser()
    parser.add_argument('--slack', action='store_true', help='Send Slack notification')
    parser.add_argument('--email', action='store_true', help='Send email notification')
    parser.add_argument('--update-snapshots', action='store_true', help='Update stored snapshots')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    # Compare rule_mapping.json
    mapping = load_file(RULE_MAPPING_PATH)
    mapping_snap = load_snapshot("rule_mapping.json")
    added, removed, changed = diff_dicts(mapping_snap or {}, mapping or {})
    # Compare .smartai_rules.yaml (line-based)
    config = load_file(RULE_CONFIG_PATH)
    config_snap = load_snapshot(".smartai_rules.yaml")
    config_diff = list(difflib.unified_diff(config_snap or [], config or [], fromfile="before", tofile="after"))
    # Prepare message
    msg = []
    if added or removed or changed:
        msg.append("Rule mapping changes detected:")
        if added:
            msg.append(f"  Added: {', '.join(added)}")
        if removed:
            msg.append(f"  Removed: {', '.join(removed)}")
        if changed:
            msg.append(f"  Modified: {', '.join(changed)}")
    if config_diff:
        msg.append("\nRule config changes detected:")
        msg.extend(config_diff)
    if not msg:
        logger.info("No rule changes detected.")
        return
    full_msg = "\n".join(msg)
    logger.info(full_msg)
    # Notify
    if args.slack:
        send_slack_notification(full_msg)
    if args.email:
        send_email_notification(subject="Rule Change Notification", body=full_msg)
    # Update snapshots if requested
    if args.update_snapshots:
        save_snapshot("rule_mapping.json", mapping)
        save_snapshot(".smartai_rules.yaml", config)
        logger.info("Snapshots updated.")

if __name__ == "__main__":
    main()
