#!/usr/bin/env python3
"""
Rule Feedback Loop
- Allows developers to provide feedback on rules (e.g., "too strict", "false positive")
- Aggregates and summarizes feedback for maintainers
Category: automation
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from pathlib import Path
from datetime import datetime
import os
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

FEEDBACK_LOG = Path(__file__).parent.parent / "logs/rule_feedback.jsonl"


def log_feedback(rule, feedback, user=None):
    entry = {
        "rule": rule,
        "feedback": feedback,
        "user": user or "anonymous",
        "timestamp": datetime.now().isoformat()
    }
    with open(FEEDBACK_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

def aggregate_feedback():
    if not FEEDBACK_LOG.exists():
        return {}
    data = {}
    with open(FEEDBACK_LOG) as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                rule = entry["rule"]
                data.setdefault(rule, []).append(entry["feedback"])
    return data

def main():
    parser = get_arg_parser()
    parser.add_argument('--submit', nargs=2, metavar=('RULE', 'FEEDBACK'), help='Submit feedback for a rule')
    parser.add_argument('--user', type=str, help='User submitting feedback')
    parser.add_argument('--summary', action='store_true', help='Show aggregated feedback summary')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    if args.submit:
        rule, feedback = args.submit
        log_feedback(rule, feedback, args.user)
        logger.info(f"Feedback submitted for {rule}: {feedback}")
    elif args.summary:
        data = aggregate_feedback()
        logger.info("Rule Feedback Summary:")
        for rule, feedbacks in data.items():
            logger.info(f"- {rule}: {len(feedbacks)} feedback entries")
            for fb in feedbacks:
                logger.info(f"    - {fb}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
