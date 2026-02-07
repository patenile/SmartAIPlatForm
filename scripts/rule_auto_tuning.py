#!/usr/bin/env python3
"""
Automated Rule Tuning
- Analyzes violation patterns and auto-tunes rule thresholds (e.g., line length, complexity)
- Suggests or applies optimal values for developer experience
Category: automation
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from pathlib import Path
from statistics import median, mean
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

VIOLATION_LOG = Path(__file__).parent.parent / "logs/rule_violations.jsonl"
RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"

# Example: rules with tunable thresholds
TUNABLES = {
    "check_py_length": "max_length",
    "check_complexity": "max_complexity",
    # Add more as needed
}

def load_violations():
    if not VIOLATION_LOG.exists():
        return []
    with open(VIOLATION_LOG) as f:
        return [json.loads(line) for line in f if line.strip()]

def main():
    parser = get_arg_parser()
    parser.add_argument('--suggest', action='store_true', help='Suggest optimal thresholds')
    parser.add_argument('--apply', action='store_true', help='Auto-tune and update rule_mapping.json')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    mapping = json.load(open(RULE_MAPPING_PATH))
    violations = load_violations()
    # Aggregate by rule/threshold
    stats = {rule: [] for rule in TUNABLES}
    for v in violations:
        rule = v.get('rule')
        if rule in TUNABLES and 'value' in v:
            stats[rule].append(v['value'])
    suggestions = {}
    for rule, values in stats.items():
        if values:
            # Suggest threshold as 90th percentile or median+10%
            values_sorted = sorted(values)
            threshold = int(mean(values) + 0.1 * mean(values))
            suggestions[rule] = threshold
            logger.info(f"Suggest {TUNABLES[rule]} for {rule}: {threshold} (based on {len(values)} violations)")
    if args.apply and suggestions:
        for rule, val in suggestions.items():
            mapping[rule]['default_settings'][TUNABLES[rule]] = val
        with open(RULE_MAPPING_PATH, "w") as f:
            json.dump(mapping, f, indent=2)
        logger.info("Rule thresholds auto-tuned and updated.")
    if not (args.suggest or args.apply):
        parser.print_help()

if __name__ == "__main__":
    main()
