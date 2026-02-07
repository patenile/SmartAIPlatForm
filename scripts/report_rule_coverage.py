#!/usr/bin/env python3
"""
Generate a report of rule coverage per file and per rule.
- Shows which files are checked by which rules, and which are skipped/suppressed.
- Outputs a Markdown table and summary.
Category: automation
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pathlib import Path
from scripts.rule_config import load_rule_config, get_file_rule_settings, is_rule_suppressed
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser

# List of all rule scripts and their rule names
RULE_SCRIPTS = [
    ("check_py_length.py", "check_py_length"),
    ("check_shebang_and_imports.py", "check_shebang"),
    ("check_shebang_and_imports.py", "check_imports_at_top"),
    ("check_dependencies.py", "check_dependencies"),
    ("check_python_utilities.py", "check_python_utilities"),
    ("setup_env.py", "setup_env"),
    ("manage_services.py", "manage_services"),
    ("check_onboarding.py", "check_onboarding"),
    ("check_docstrings.py", "check_docstrings"),
]


def main():
    parser = get_arg_parser()
    parser.add_argument('--report', type=str, default="markdown", choices=["markdown", "plain"], help="Output format")
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    config = load_rule_config()
    root = Path(__file__).parent.parent
    py_files = sorted([f for f in root.glob('**/*.py') if 'plugins/' not in str(f)])
    # Build coverage matrix: file -> rule -> status
    coverage = {}
    for py_file in py_files:
        rel = str(py_file.relative_to(root))
        coverage[rel] = {}
        for script, rule in RULE_SCRIPTS:
            settings = get_file_rule_settings(py_file, config)
            suppressed, reason = is_rule_suppressed(rule, config, py_file)
            if suppressed:
                coverage[rel][rule] = f"suppressed ({reason})" if reason else "suppressed"
            elif rule in (settings.get('skip_rules') or []):
                coverage[rel][rule] = "skipped"
            else:
                coverage[rel][rule] = "checked"
    # Output report
    rules = [r for _, r in RULE_SCRIPTS]
    if args.report == "markdown":
        header = "| File | " + " | ".join(rules) + " |"
        sep = "|---" * (len(rules)+1) + "|"
        logger.info(header)
        logger.info(sep)
        for f, row in coverage.items():
            logger.info("| " + f + " | " + " | ".join(row[r] for r in rules) + " |")
    else:
        for f, row in coverage.items():
            logger.info(f"{f}:")
            for r in rules:
                logger.info(f"  {r}: {row[r]}")
    # Summary
    checked_count = sum(row[r] == "checked" for row in coverage.values() for r in rules)
    total = len(coverage) * len(rules)
    logger.info(f"\nRule coverage: {checked_count}/{total} checks active ({checked_count*100//total if total else 0}%)")

if __name__ == "__main__":
    main()
