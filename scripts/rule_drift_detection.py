#!/usr/bin/env python3
"""
Rule Drift Detection
- Alerts if code diverges from enforced rules over time
- Compares current violations to historical baseline
- Notifies if drift increases or new violations appear
Category: automation
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from pathlib import Path
import os
from datetime import datetime
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
from scripts.notify_slack import send_slack_notification
from scripts.notify_email import send_email_notification

LOGS_DIR = Path(__file__).parent.parent / "logs"
VIOLATION_LOG = LOGS_DIR / "rule_violations.jsonl"
DRIFT_BASELINE = LOGS_DIR / "rule_drift_baseline.json"


def load_violations():
    if not VIOLATION_LOG.exists():
        return []
    with open(VIOLATION_LOG) as f:
        return [json.loads(line) for line in f if line.strip()]

def load_baseline():
    if DRIFT_BASELINE.exists():
        with open(DRIFT_BASELINE) as f:
            return json.load(f)
    return {}

def save_baseline(data):
    with open(DRIFT_BASELINE, "w") as f:
        json.dump(data, f, indent=2)

def main():
    parser = get_arg_parser()
    parser.add_argument('--update-baseline', action='store_true', help='Update drift baseline to current violations')
    parser.add_argument('--slack', action='store_true', help='Notify via Slack if drift detected')
    parser.add_argument('--email', action='store_true', help='Notify via email if drift detected')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    violations = load_violations()
    baseline = load_baseline()
    # Aggregate by rule/file
    current = {}
    for v in violations:
        key = (v['rule'], v['file'])
        current[key] = current.get(key, 0) + 1
    drift = []
    for key, count in current.items():
        base = baseline.get(str(key), 0)
        if count > base:
            drift.append((key, base, count))
    if drift:
        msg = [f"Rule drift detected at {datetime.now().isoformat()}:"]
        for (rule, file), base, now in drift:
            msg.append(f"- {rule} in {file}: {now} violations (was {base})")
        full_msg = "\n".join(msg)
        logger.info(full_msg)
        if args.slack:
            send_slack_notification(full_msg)
        if args.email:
            send_email_notification(subject="Rule Drift Detected", body=full_msg)
    else:
        logger.info("No rule drift detected.")
    if args.update_baseline:
        save_baseline({str(k): v for k, v in current.items()})
        logger.info("Drift baseline updated.")

if __name__ == "__main__":
    main()
