#!/usr/bin/env python3
"""
Automated Rule Performance Profiling
- Tracks and reports the runtime/performance impact of each rule
- Aggregates timing data from all rule scripts
- Alerts if a rule becomes a bottleneck
Category: automation
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
import time
from pathlib import Path
from collections import defaultdict
import os
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

LOGS_DIR = Path(__file__).parent.parent / "logs"
PERF_LOG = LOGS_DIR / "rule_performance.jsonl"
RULES_DIR = Path(__file__).parent
RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"


def log_performance(rule, duration):
    LOGS_DIR.mkdir(exist_ok=True)
    with open(PERF_LOG, "a") as f:
        f.write(json.dumps({"rule": rule, "duration": duration, "ts": time.time()}) + "\n")

def aggregate_performance():
    if not PERF_LOG.exists():
        return {}
    data = defaultdict(list)
    with open(PERF_LOG) as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                data[entry["rule"]].append(entry["duration"])
    return {rule: sum(times)/len(times) for rule, times in data.items()}

def main():
    parser = get_arg_parser()
    parser.add_argument('--profile', type=str, help='Profile a rule script (by name)')
    parser.add_argument('--aggregate', action='store_true', help='Show aggregated performance report')
    parser.add_argument('--alert-threshold', type=float, default=2.0, help='Alert if rule avg runtime exceeds this (seconds)')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    if args.profile:
        script = RULES_DIR / args.profile
        if not script.exists():
            logger.error(f"Script {args.profile} not found.")
            sys.exit(1)
        start = time.time()
        exit_code = sys.call([sys.executable, str(script)])
        duration = time.time() - start
        log_performance(args.profile, duration)
        logger.info(f"Profiled {args.profile}: {duration:.2f}s (exit {exit_code})")
    elif args.aggregate:
        perf = aggregate_performance()
        logger.info("Rule | Avg Runtime (s)")
        logger.info("-----|---------------")
        for rule, avg in sorted(perf.items(), key=lambda x: -x[1]):
            logger.info(f"{rule} | {avg:.2f}")
        # Alert if any rule exceeds threshold
        for rule, avg in perf.items():
            if avg > args.alert_threshold:
                logger.warning(f"ALERT: {rule} avg runtime {avg:.2f}s exceeds threshold {args.alert_threshold}s!")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
