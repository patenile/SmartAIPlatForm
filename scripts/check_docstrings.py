#!/usr/bin/env python3
"""
Check for missing or invalid docstrings in Python files.
Category: docs
"""
import sys
import os
from pathlib import Path
import ast
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
from scripts.rule_config import load_rule_config, get_file_rule_settings, is_rule_suppressed

def has_module_docstring(tree):
    return ast.get_docstring(tree) is not None

def main():
    root = Path(__file__).parent.parent
    py_files = list(root.glob('**/*.py'))
    failed = False
    for py_file in py_files:
        with open(py_file, encoding='utf-8') as f:
            source = f.read()
        try:
            tree = ast.parse(source)
        except Exception as e:
            print(f"ERROR: {py_file} could not be parsed: {e}")
            failed = True
            continue
        if not has_module_docstring(tree):
            print(f"ERROR: {py_file} is missing a module docstring.")
            failed = True
    if failed:
        sys.exit(1)
    print("All Python files have module docstrings.")

if __name__ == "__main__":
    def main():
        parser = get_arg_parser()
        parser.add_argument('--autofix', action='store_true', help='Auto-fix missing docstrings (stub)')
        parser.add_argument('--dry-run', action='store_true', help='Preview auto-fix changes')
        args = parser.parse_args()
        logger = get_logger(debug=args.debug)
        config = load_rule_config()
        script_path = Path(__file__).resolve()
        settings = get_file_rule_settings(script_path, config)
        suppressed, reason = is_rule_suppressed('check_docstrings', config, script_path)
        if suppressed:
            logger.info(f"[suppressed] Skipping check_docstrings for {script_path} (reason: {reason})")
            return
        if 'check_docstrings' in (settings.get('skip_rules') or []):
            logger.info(f"[selective enforcement] Skipping check_docstrings for {script_path}")
            return
        try:
            root = Path(__file__).parent.parent
            py_files = list(root.glob('**/*.py'))
            failed = False
            for py_file in py_files:
                try:
                    with open(py_file, encoding='utf-8') as f:
                        tree = ast.parse(f.read(), filename=str(py_file))
                    if not ast.get_docstring(tree):
                        if args.autofix or args.dry_run:
                            if args.dry_run:
                                logger.info(f"[dry-run] Would add module docstring to {py_file}")
                            else:
                                logger.info(f"Auto-fix: Please manually add a module docstring to {py_file}")
                        else:
                            logger.error(f"{py_file} is missing a module docstring.")
                            failed = True
                except Exception as e:
                    logger.error(f"Exception in {py_file}: {e}")
                    failed = True
            if args.autofix or args.dry_run:
                return
            if failed:
                sys.exit(1)
            logger.info("All files have module docstrings.")
        except Exception as e:
            logger.error(f"Exception in check_docstrings: {e}")
            sys.exit(1)
