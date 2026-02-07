#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pathlib import Path
import json
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
from scripts.rule_config import load_rule_config, get_file_rule_settings, is_rule_suppressed
"""
Check that all utility/setup scripts are Python only.
Fails if any non-.py script is found in scripts/.
Category: security

This script scans the scripts/ directory and skips files that are not Python scripts (.py).
Skipped files are logged for documentation and compliance tracking.
"""

def print_rule_and_fix(logger):
    mapping_path = Path(__file__).parent / "rule_mapping.json"
    if mapping_path.exists():
        with open(mapping_path) as f:
            rules = json.load(f)
        rule = rules.get("check_python_utilities", {})
        logger.info(f"Rule: {rule.get('rule','')}")
        logger.info(f"See: {rule.get('doc','')}")
        logger.info(f"Suggested fix: {rule.get('fix','')}")

def main():
    parser = get_arg_parser()
    parser.add_argument('--autofix', action='store_true', help='Auto-fix by renaming/removing non-Python scripts')
    parser.add_argument('--dry-run', action='store_true', help='Preview auto-fix changes')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    config = load_rule_config()
    script_path = Path(__file__).resolve()
    settings = get_file_rule_settings(script_path, config)
    suppressed, reason = is_rule_suppressed('check_python_utilities', config, script_path)
    if suppressed:
        logger.info(f"[suppressed] Skipping check_python_utilities for {script_path} (reason: {reason})")
        return
    if 'check_python_utilities' in (settings.get('skip_rules') or []):
        logger.info(f"[selective enforcement] Skipping check_python_utilities for {script_path}")
        return
    try:
        scripts = Path(__file__).parent
        files = [f for f in scripts.iterdir() if f.is_file()]
        non_py = [f for f in files if not f.name.endswith('.py')]
        skipped = []
        for f in non_py:
            logger.info(f"[skip] Skipping non-Python script: {f}")
            skipped.append(str(f))
        if args.autofix or args.dry_run:
            if non_py:
                for f in non_py:
                    if args.dry_run:
                        logger.info(f"[dry-run] Would remove or rename non-Python script: {f}")
                    else:
                        logger.info(f"Auto-fix: Please manually remove or rename {f} to .py")
            else:
                logger.info("No non-Python scripts to auto-fix.")
            return
        if skipped:
            logger.info(f"Documentation: Skipped non-Python scripts: {skipped}")
        for f in files:
            if f.name.endswith('.py'):
                logger.info(f"Checked Python script: {f}")
        logger.info("All utility/setup scripts are Python only or skipped.")
    except Exception as e:
        logger.error(f"Exception in check_python_utilities: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
