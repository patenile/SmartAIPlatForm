#!/usr/bin/env python3
"""
Check for shebang and import grouping rules in Python files.
- Fails if any .py file is missing a shebang (#!) as the first line.
- Fails if any import is not at the top (after shebang and docstring/comments).
Category: modularity
"""


import sys
import os
from pathlib import Path
import re
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.rule_config import load_rule_config, get_file_rule_settings, is_rule_suppressed
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser

def print_rule_and_fix(rule_key, logger):
    mapping_path = Path(__file__).parent / "rule_mapping.json"
    if mapping_path.exists():
        with open(mapping_path) as f:
            rules = json.load(f)
        rule = rules.get(rule_key, {})
        logger.info(f"Rule: {rule.get('rule','')}")
        logger.info(f"See: {rule.get('doc','')}")
        logger.info(f"Suggested fix: {rule.get('fix','')}")

def check_shebang(py_file, logger):
    try:
        config = load_rule_config()
        settings = get_file_rule_settings(Path(py_file), config)
        if 'check_shebang' in (settings.get('skip_rules') or []):
            return True
        with open(py_file, encoding='utf-8') as f:
            lines = f.readlines()
        # Find first non-empty, non-comment line (allow comments/blank lines before shebang)
        for idx, line in enumerate(lines):
            if line.strip() == '' or (line.strip().startswith('#') and not line.startswith('#!')):
                continue
            if line.startswith('#!'):
                return True
            else:
                logger.error(f"{py_file} is missing a shebang (#!) as the first non-comment line (line {idx+1}).")
                print_rule_and_fix("check_shebang", logger)
                return False
        # If file is empty or only comments, treat as missing shebang
        logger.error(f"{py_file} is missing a shebang (#!) as the first non-comment line.")
        print_rule_and_fix("check_shebang", logger)
        return False
    except Exception as e:
        logger.error(f"Exception in check_shebang: {e}")
        return False

def check_imports_at_top(py_file, logger):
    try:
        config = load_rule_config()
        settings = get_file_rule_settings(Path(py_file), config)
        if 'check_imports_at_top' in (settings.get('skip_rules') or []):
            return True
        with open(py_file, encoding='utf-8') as f:
            lines = f.readlines()
        # Find shebang (allow comments/blank lines before shebang)
        i = 0
        while i < len(lines):
            if lines[i].strip() == '' or (lines[i].strip().startswith('#') and not lines[i].startswith('#!')):
                i += 1
                continue
            if lines[i].startswith('#!'):
                i += 1
                break
            else:
                break
        # Allow docstring after shebang
        if i < len(lines) and re.match(r'\s*[\'\"]{3}', lines[i]):
            docstring_delim = lines[i][:3]
            i += 1
            while i < len(lines) and docstring_delim not in lines[i]:
                i += 1
            i += 1  # skip closing docstring
        # Allow comments/whitespace between shebang/docstring and imports
        while i < len(lines):
            if lines[i].strip() == '' or lines[i].strip().startswith('#'):
                i += 1
                continue
            if lines[i].startswith('import ') or lines[i].startswith('from '):
                break
            else:
                break
        # Collect all imports
        import_end = i
        while import_end < len(lines):
            if lines[import_end].startswith('import ') or lines[import_end].startswith('from '):
                import_end += 1
            elif lines[import_end].strip() == '' or lines[import_end].strip().startswith('#'):
                import_end += 1
            else:
                break
        # Allow imports anywhere before first class, def, or variable assignment
        code_started = False
        for j, line in enumerate(lines):
            # Ignore comments and blank lines
            if line.strip() == '' or line.strip().startswith('#'):
                continue
            # If we see class, def, or variable assignment, code has started
            if re.match(r'\s*(class |def |\w+\s*=)', line):
                code_started = True
            # If code has started, imports are not allowed
            if code_started and (line.startswith('import ') or line.startswith('from ')):
                logger.error(f"{py_file} has import not at the top (line {j+1}).")
                print_rule_and_fix("check_imports_at_top", logger)
                return False
        return True
    except Exception as e:
        logger.error(f"Exception in check_imports_at_top: {e}")
        return False

def autofix_shebang_and_imports(py_file, logger, dry_run=False):
    try:
        with open(py_file, encoding='utf-8') as f:
            lines = f.readlines()
        changed = False
        # Ensure shebang
        if not lines or not lines[0].startswith('#!'):
            lines = ['#!/usr/bin/env python3\n'] + lines
            changed = True
        # Move all imports to the top after shebang and docstring/comments
        i = 1
        if i < len(lines) and re.match(r'\s*[\'\"]{3}', lines[i]):
            docstring_delim = lines[i][:3]
            i += 1
            while i < len(lines) and docstring_delim not in lines[i]:
                i += 1
            i += 1
        while i < len(lines) and (lines[i].strip() == '' or lines[i].strip().startswith('#')):
            i += 1
        # Collect imports
        import_lines = []
        rest = []
        for idx, line in enumerate(lines[i:], start=i):
            if line.startswith('import ') or line.startswith('from '):
                import_lines.append(line)
                changed = True
            else:
                rest.append(line)
        new_lines = lines[:i] + import_lines + rest
        if changed:
            if dry_run:
                logger.info(f"[dry-run] Would auto-fix {py_file}")
            else:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                logger.info(f"Auto-fixed {py_file}")
    except Exception as e:
        logger.error(f"Exception in autofix_shebang_and_imports: {e}")

def main():
    parser = get_arg_parser()
    parser.add_argument('--autofix', action='store_true', help='Auto-fix shebang/import grouping')
    parser.add_argument('--dry-run', action='store_true', help='Preview auto-fix changes')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    config = load_rule_config()
    script_path = Path(__file__).resolve()
    settings = get_file_rule_settings(script_path, config)
    # Suppression for both rules
    suppressed_shebang, reason_shebang = is_rule_suppressed('check_shebang', config, script_path)
    suppressed_imports, reason_imports = is_rule_suppressed('check_imports_at_top', config, script_path)
    skip_shebang = 'check_shebang' in (settings.get('skip_rules') or []) or suppressed_shebang
    skip_imports = 'check_imports_at_top' in (settings.get('skip_rules') or []) or suppressed_imports
    if skip_shebang and skip_imports:
        logger.info(f"[suppressed/selective enforcement] Skipping check_shebang and check_imports_at_top for {script_path}")
        return
    root = Path(__file__).parent.parent
    py_files = list(root.glob('**/*.py'))
    failed = False
    skip_patterns = [".venv", "site-packages", "__pycache__", "env", "build", "dist"]
    for py_file in py_files:
        # Skip files in virtual environment or build folders
        rel_path = str(py_file)
        if any(pat in rel_path for pat in skip_patterns):
            continue
        file_settings = get_file_rule_settings(py_file, config)
        suppressed_shebang_file, reason_shebang_file = is_rule_suppressed('check_shebang', config, py_file)
        suppressed_imports_file, reason_imports_file = is_rule_suppressed('check_imports_at_top', config, py_file)
        skip_shebang_file = 'check_shebang' in (file_settings.get('skip_rules') or []) or suppressed_shebang_file
        skip_imports_file = 'check_imports_at_top' in (file_settings.get('skip_rules') or []) or suppressed_imports_file
        if args.autofix or args.dry_run:
            if not (skip_shebang_file and skip_imports_file):
                autofix_shebang_and_imports(py_file, logger, dry_run=args.dry_run)
        else:
            if not skip_shebang_file:
                if not check_shebang(py_file, logger):
                    failed = True
            if not skip_imports_file:
                if not check_imports_at_top(py_file, logger):
                    failed = True
    if not (args.autofix or args.dry_run):
        if failed:
            logger.error("Some Python files are missing shebang or have misplaced imports.")
            sys.exit(1)
        logger.info("All Python files have a shebang and all imports are at the top.")

if __name__ == "__main__":
    main()
