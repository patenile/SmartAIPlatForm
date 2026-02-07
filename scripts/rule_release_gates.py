#!/usr/bin/env python3
"""
Rule-Based Release Gates
- Blocks releases if critical rules are violated, with override/escalation workflow
- Integrates with CI/CD to enforce gates
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

VIOLATION_LOG = Path(__file__).parent.parent / "logs/rule_violations.jsonl"
RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"


def load_violations():
    if not VIOLATION_LOG.exists():
        return []
    with open(VIOLATION_LOG) as f:
        return [json.loads(line) for line in f if line.strip()]

def main():
    parser = get_arg_parser()
    parser.add_argument('--enforce', action='store_true', help='Block release if critical rules are violated')
    parser.add_argument('--override', action='store_true', help='Override gate and allow release')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    mapping = json.load(open(RULE_MAPPING_PATH))
    violations = load_violations()
    critical_rules = [r for r, meta in mapping.items() if meta.get('severity', 'error') == 'error' and meta.get('enforcement', 'block') == 'block']
    critical_violations = [v for v in violations if v['rule'] in critical_rules]
    if args.enforce:
        if critical_violations and not args.override:
            logger.error(f"Release blocked: {len(critical_violations)} critical rule violations found.")
            sys.exit(1)
        elif critical_violations and args.override:
            logger.warning(f"Release override: {len(critical_violations)} critical rule violations present.")
        else:
            logger.info("No critical rule violations. Release allowed.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
