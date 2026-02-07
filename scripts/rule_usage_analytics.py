#!/usr/bin/env python3
"""
Rule Usage Analytics Dashboard
- Aggregates and visualizes rule usage and violation trends
- Generates a Markdown/HTML dashboard with stats and charts
- Tracks: violations per rule, auto-fix rates, trends over time
Category: automation
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import os
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

LOGS_DIR = Path(__file__).parent.parent / "logs"
DASHBOARD_MD = Path(__file__).parent.parent / "docs/rule_usage_dashboard.md"

# Assumes each check script logs violations to logs/rule_violations.jsonl (one JSON per line)
VIOLATION_LOG = LOGS_DIR / "rule_violations.jsonl"


def load_violations():
    if not VIOLATION_LOG.exists():
        return []
    with open(VIOLATION_LOG) as f:
        return [json.loads(line) for line in f if line.strip()]

def main():
    parser = get_arg_parser()
    parser.add_argument('--update-dashboard', action='store_true', help='Update Markdown dashboard')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    violations = load_violations()
    if not violations:
        logger.info("No rule violation data found.")
        return
    # Aggregate stats
    by_rule = Counter(v['rule'] for v in violations)
    by_file = Counter(v['file'] for v in violations)
    by_date = Counter(v.get('date', 'unknown') for v in violations)
    auto_fixed = sum(1 for v in violations if v.get('auto_fixed'))
    total = len(violations)
    # Markdown dashboard
    lines = [
        "# Rule Usage Analytics Dashboard\n",
        f"Last updated: {datetime.now().isoformat()}\n",
        f"**Total violations:** {total}",
        f"**Auto-fix rate:** {auto_fixed}/{total} ({(auto_fixed*100//total) if total else 0}%)\n",
        "## Violations per Rule\n",
        "| Rule | Violations |",
        "|---|---|",
    ]
    for rule, count in by_rule.most_common():
        lines.append(f"| {rule} | {count} |")
    lines += [
        "\n## Violations per File\n",
        "| File | Violations |",
        "|---|---|",
    ]
    for file, count in by_file.most_common()[:20]:
        lines.append(f"| {file} | {count} |")
    lines += [
        "\n## Violations Over Time\n",
        "| Date | Violations |",
        "|---|---|",
    ]
    for date, count in sorted(by_date.items()):
        lines.append(f"| {date} | {count} |")
    DASHBOARD_MD.write_text('\n'.join(lines))
    logger.info(f"Dashboard updated: {DASHBOARD_MD}")

if __name__ == "__main__":
    main()
