#!/usr/bin/env python3
"""
Pre-commit hook and test to enforce Python script length constraint.
- Fails if any .py file exceeds 350 lines (+/- 10%).
- Suggests modularization if limit is exceeded.
- Can be used as a pre-commit hook or CI test.
Category: modularity
"""
import os
import sys
import pathlib
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.rule_config import load_rule_config, get_file_rule_settings, is_rule_suppressed
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser

TOLERANCE = 0.10  # 10% tolerance for file length
def print_rule_and_fix(logger):
    mapping_path = pathlib.Path(__file__).parent / "rule_mapping.json"
    if mapping_path.exists():
        with open(mapping_path) as f:
            rules = json.load(f)
        rule = rules.get("check_py_length", {})
        logger.info(f"Rule: {rule.get('rule','')}")
        logger.info(f"See: {rule.get('doc','')}")
        logger.info(f"Suggested fix: {rule.get('fix','')}")

def check_file_length(py_file, logger, config):
    try:
        # Skip files in .venv or site-packages
        if ".venv" in str(py_file) or "site-packages" in str(py_file):
            return True
        settings = get_file_rule_settings(pathlib.Path(py_file), config)
        if 'check_py_length' in (settings.get('skip_rules') or []):
            return True
        max_lines = settings.get('max_file_length', 350)
        min_lines = int(max_lines * (1 - TOLERANCE))
        max_allowed = int(max_lines * (1 + TOLERANCE))
        with open(py_file, encoding='utf-8') as f:
            lines = f.readlines()
        n = len(lines)
        if n > max_allowed:
            logger.error(f"{py_file} has {n} lines (limit: {max_lines} ±10%). Please modularize.")
            print_rule_and_fix(logger)
            return False
        return True
    except Exception as e:
        logger.error(f"Exception in check_file_length: {e}")
        return False


def autofix_py_length(py_file, logger, max_lines=350, dry_run=False):
    try:
        with open(py_file, encoding='utf-8') as f:
            lines = f.readlines()
        n = len(lines)
        if n > max_lines:
            # Try to split the file at the last function/class before the limit
            split_idx = max_lines
            for i in range(max_lines-1, 0, -1):
                if lines[i].startswith('def ') or lines[i].startswith('class '):
                    split_idx = i
                    break
            part1 = lines[:split_idx]
            part2 = lines[split_idx:]
            if dry_run:
                logger.info(f"[dry-run] Would split {py_file} at line {split_idx} (file has {n} lines)")
            else:
                with open(py_file.replace('.py', '_part1.py'), 'w', encoding='utf-8') as f1:
                    f1.writelines(part1)
                with open(py_file.replace('.py', '_part2.py'), 'w', encoding='utf-8') as f2:
                    f2.writelines(part2)
                logger.info(f"Auto-split {py_file} into {py_file.replace('.py', '_part1.py')} and _part2.py")
    except Exception as e:
        logger.error(f"Exception in autofix_py_length: {e}")


def main():
    parser = get_arg_parser()
    parser.add_argument('--autofix', action='store_true', help='Auto-fix file length by splitting')
    parser.add_argument('--dry-run', action='store_true', help='Preview auto-fix changes')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    config = load_rule_config()
    script_path = pathlib.Path(__file__).resolve()
    settings = get_file_rule_settings(script_path, config)
    suppressed, reason = is_rule_suppressed('check_py_length', config, script_path)
    if suppressed:
        logger.info(f"[suppressed] Skipping check_py_length for {script_path} (reason: {reason})")
        return
    if 'check_py_length' in (settings.get('skip_rules') or []):
        logger.info(f"[selective enforcement] Skipping check_py_length for {script_path}")
        return
    root = pathlib.Path(__file__).parent.parent
    py_files = list(root.glob('**/*.py'))
    failed = False
    for py_file in py_files:
        settings = get_file_rule_settings(py_file, config)
        max_lines = settings.get('max_file_length', 350)
        if args.autofix or args.dry_run:
            autofix_py_length(str(py_file), logger, max_lines=max_lines, dry_run=args.dry_run)
        else:
            if not check_file_length(py_file, logger, config):
                failed = True
    if not (args.autofix or args.dry_run):
        if failed:
            logger.error("Some Python files exceed the allowed line count.")
            sys.exit(1)
        logger.info("All Python files are within the allowed line count.")

if __name__ == "__main__":
    main()
